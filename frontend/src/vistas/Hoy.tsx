import { Link } from 'react-router-dom'
import { useHoy } from '../lib/api'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { SignalBadge } from '../componentes/SignalBadge'
import { Sparkline } from '../componentes/Sparkline'
import { NewsSentiment } from '../componentes/NewsSentiment'
import { Cargando, EmptyState, ErrorCarga } from '../componentes/EmptyState'
import { distanciaHumana, fechaCorta, horaChile } from '../lib/tiempo'
import { rangoIntervalo80 } from '../lib/formato'

// Umbrales documentados del Roca→Chip (DECISIONES.md 4.7.1): solo la cifra
// principal toma color, y solo al cruzarlos — frío <30, caliente >70.
const tonoRoca = (v: number): 'frio' | 'caliente' | 'neutro' =>
  v < 30 ? 'frio' : v > 70 ? 'caliente' : 'neutro'

// ============================================================
// /hoy — el portal. Responde en un vistazo: ¿en qué régimen estamos,
// qué pasó en NY, qué señales hay y cuál es la próxima apertura que
// esas señales intentan anticipar?
// ============================================================

export function Hoy() {
  const { data, isLoading, error } = useHoy()

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <Cargando alto="h-24" />
        <Cargando alto="h-48" />
        <Cargando alto="h-48" />
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} />
  if (!data) return null
  const d = data.datos

  return (
    <div className="mx-auto grid max-w-6xl grid-cols-1 gap-4 lg:grid-cols-3">
      {/* fila 1: el estado del mundo en 4 cifras */}
      <Card className="lg:col-span-3">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          <StatTile
            etiqueta="Régimen (SOX)"
            valor={d.regimen?.etiqueta ?? 'sin datos'}
            detalle={
              d.regimen
                ? `MA50/MA200 ${d.regimen.ratio_ma_pct >= 0 ? '+' : ''}${d.regimen.ratio_ma_pct}% · vol ${d.regimen.vol_actual}% vs mediana ${d.regimen.vol_mediana}%`
                : undefined
            }
          />
          <StatTile
            etiqueta="SOX último cierre"
            valor={d.sox ? `${d.sox.mov_pct >= 0 ? '+' : ''}${d.sox.mov_pct}` : '—'}
            sufijo="%"
            tono={d.sox ? (d.sox.mov_pct >= 0 ? 'pos' : 'neg') : 'neutro'}
            detalle={
              d.sox
                ? d.sox.feriado_hoy
                  ? `feriado en EE.UU. — último movimiento real: ${fechaCorta(d.sox.fecha)}`
                  : fechaCorta(d.sox.fecha)
                : undefined
            }
          />
          <div className="flex items-end gap-3">
            <StatTile
              etiqueta="Roca→Chip"
              valor={d.roca_chip?.valor ?? '—'}
              tono={d.roca_chip ? tonoRoca(d.roca_chip.valor) : 'neutro'}
              detalle={
                d.roca_chip
                  ? `percentil 1 año · sellado ${fechaCorta(d.roca_chip.fecha)}`
                  : 'sin snapshot sellado aún'
              }
              tooltip="Valor sellado del último snapshot — no se recalcula al visitar. 0 = cadena fría · 100 = caliente; la cifra toma color bajo 30 o sobre 70."
            />
            {d.roca_chip && <Sparkline valores={d.roca_chip.historia} />}
          </div>
          <StatTile
            etiqueta="Sentimiento sector"
            valor={
              d.sentimiento_sector != null
                ? `${d.sentimiento_sector >= 0 ? '+' : ''}${d.sentimiento_sector.toFixed(2)}`
                : '—'
            }
            tono={
              d.sentimiento_sector == null
                ? 'neutro'
                : d.sentimiento_sector > 0.15
                  ? 'pos'
                  : d.sentimiento_sector < -0.15
                    ? 'neg'
                    : 'neutro'
            }
            detalle="noticias ponderadas por frescura y relevancia"
          />
        </div>
      </Card>

      {/* protagonista: la próxima apertura que las señales anticipan */}
      <Card
        titulo="Próxima apertura"
        className="lg:col-span-2"
        accion={
          d.proxima_apertura && (
            <span className="num text-[11px] text-text-3">
              {horaChile(d.proxima_apertura.apertura_utc)} Chile ·{' '}
              {distanciaHumana(d.proxima_apertura.apertura_utc)}
            </span>
          )
        }
      >
        {d.proxima_apertura ? (
          <>
            <p className="mb-3 text-[13px] text-text-2">
              {d.proxima_apertura.nombre} — sesión del{' '}
              <span className="num">{d.proxima_apertura.sesion}</span>
            </p>
            {d.proxima_apertura.predicciones.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {d.proxima_apertura.predicciones.map((p) => (
                  <SignalBadge
                    key={p.ticker}
                    titulo={`${p.nombre} ${p.estimado_pct >= 0 ? '+' : ''}${p.estimado_pct.toFixed(2)}%`}
                    direccion={p.estimado_pct >= 0 ? 'pos' : 'neg'}
                    magnitud={rangoIntervalo80(p.estimado_pct, p.intervalo80_pp)}
                    porque={`β=${p.beta.toFixed(2)} sobre el último movimiento real del SOX${p.zona_earnings ? ` · zona de earnings (${p.dias_earnings}d)` : ''}`}
                    nMuestra={p.n_muestra}
                    r2={p.r2_historico}
                    emitidaUtc={p.emitida_utc}
                  />
                ))}
              </div>
            ) : (
              <EmptyState titulo="Sin predicciones para este exchange" />
            )}
          </>
        ) : (
          <EmptyState titulo="Sin sesión próxima identificable" />
        )}
      </Card>

      {/* track record — celdas vacías con naturalidad, nunca escondidas */}
      <Card titulo="Track record (30d)">
        {d.track_record.suficiente ? (
          <div className="grid grid-cols-2 gap-4">
            <StatTile
              etiqueta="Acierto gap"
              valor={`${d.track_record.gap!.pct_aciertos}%`}
              detalle={`MAE ${d.track_record.gap!.mae_pp} pp · n=${d.track_record.n}`}
            />
            <StatTile
              etiqueta="Acierto sesión"
              valor={`${d.track_record.retorno_sesion!.pct_aciertos}%`}
              detalle={`MAE ${d.track_record.retorno_sesion!.mae_pp} pp · n=${d.track_record.n}`}
            />
          </div>
        ) : (
          <EmptyState
            titulo={`En maduración: ${d.track_record.n}/${d.track_record.minimo}`}
            detalle="Las predicciones selladas aún no acumulan verificaciones suficientes. Se muestra tal cual — sin datos no hay métrica."
          />
        )}
      </Card>

      {/* señales del día */}
      <Card titulo="Señales del día" className="lg:col-span-2">
        {d.senales_dia.length > 0 ? (
          <div className="grid gap-3">
            {d.senales_dia.map((s, i) => (
              <SignalBadge
                key={i}
                titulo={s.titulo}
                direccion={s.direccion}
                magnitud={s.magnitud}
                porque={s.porque}
                nMuestra={s.n_muestra}
                r2={s.r2_historico}
                emitidaUtc={s.emitida_utc}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            titulo="Sin señales activas hoy"
            detalle="Ningún umbral se cruzó. Un día sin señales es un dato, no un error."
          />
        )}
      </Card>

      {/* resumen IA + titulares */}
      <Card titulo="Noticias">
        {d.resumen_ia && (
          <p className="mb-3 border-b border-border pb-3 text-xs leading-relaxed text-text-2">
            {d.resumen_ia}
          </p>
        )}
        {d.noticias_top.length > 0 ? (
          <>
            <NewsSentiment titulares={d.noticias_top} />
            <Link
              to="/analisis"
              className="mt-2 block text-[11px] text-text-3 hover:text-text-2"
            >
              ver análisis completo →
            </Link>
          </>
        ) : (
          <EmptyState
            titulo="Sin titulares relevantes hoy"
            detalle="La portada filtra el ruido (relevancia bajo 0.5). El flujo completo, con todo, vive en Análisis IA."
          />
        )}
      </Card>
    </div>
  )
}
