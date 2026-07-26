import { useSalud } from '../lib/api'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { EmptyState, ErrorCarga, EsqueletoCard, EsqueletoTiles } from '../componentes/EmptyState'
import { fechaHoraChile } from '../lib/tiempo'

// ============================================================
// /salud — la sala de máquinas visible (Etapa 5.0 WS4).
// Estado operacional del día: los 5 jobs con su resultado según sus
// ARTEFACTOS (sello, ledger de costos, logs, git), la salud de descarga
// sellada de la semana, verificaciones pendientes/atascadas, gasto de IA
// contra presupuesto y tamaños de las bases. Todo lectura — igual que el
// vigía, esta vista no corrige nada.
// ============================================================

const NOMBRE_JOB: Record<string, string> = {
  noticias: 'Noticias (RSS + IA)',
  snapshot: 'Snapshot sellado',
  reporte: 'Reporte Telegram',
  backup: 'Backup git de CSVs',
  vigia: 'Vigía',
}

function bytesLegibles(b: number): string {
  if (b >= 1024 * 1024) return `${(b / 1024 / 1024).toFixed(1)} MB`
  return `${Math.round(b / 1024)} KB`
}

export function Salud() {
  const { data, isLoading, error, refetch } = useSalud()

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <EsqueletoTiles />
        <EsqueletoCard alto="h-56" />
        <div className="grid gap-4 lg:grid-cols-2">
          <EsqueletoCard alto="h-48" />
          <EsqueletoCard alto="h-48" />
        </div>
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const op = data.datos.operacion
  const snap = data.datos.snapshot
  const pres = op.presupuesto
  const descargaHoy =
    snap?.descarga_ok != null && snap.descarga_total != null
      ? `${snap.descarga_ok}/${snap.descarga_total}`
      : null

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* el día operativo en 4 cifras */}
      <Card className="capa-1">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          <StatTile
            etiqueta="Snapshot de hoy"
            valor={snap ? fechaHoraChile(snap.timestamp_utc).split(' ')[1] ?? 'sellado' : 'sin sello'}
            detalle={
              snap
                ? `origen ${snap.origen} · modelo v${snap.modelo_version}`
                : op.es_dia_habil
                  ? 'se sella a las 18:15 (launchd) o al abrir Streamlit'
                  : 'fin de semana — el job no corre hoy'
            }
          />
          <StatTile
            etiqueta="Descarga sellada"
            valor={descargaHoy ?? '—'}
            detalle={
              descargaHoy == null
                ? snap
                  ? 'sello pre-5.0: sin dato de salud'
                  : 'sin snapshot que medir'
                : snap!.descarga_caidos
                  ? `caídos: ${snap!.descarga_caidos}`
                  : 'lote completo'
            }
          />
          <StatTile
            etiqueta="Gasto IA hoy"
            valor={`$${pres.gasto_usd.toFixed(2)}`}
            detalle={`tope $${pres.tope_usd.toFixed(2)} · mes $${pres.gasto_mes_usd.toFixed(2)}${
              pres.agotado ? ' · FRENO ACTIVO' : ''
            }`}
          />
          <StatTile
            etiqueta="Bases de datos"
            valor={bytesLegibles(op.dbs.reduce((s, d) => s + d.bytes, 0))}
            detalle={op.dbs.map((d) => `${d.nombre} ${bytesLegibles(d.bytes)}`).join(' · ')}
          />
        </div>
      </Card>

      {/* los 5 jobs del día */}
      <Card titulo="Jobs del día (lunes a viernes)" className="capa-2">
        {!op.es_dia_habil && (
          <p className="mb-2 text-[11px] text-text-3">
            Hoy es fin de semana: los jobs no corren y su estado se muestra en
            gris, no como falla.
          </p>
        )}
        <ul className="divide-y divide-border">
          {op.jobs.map((j) => {
            const punto = !op.es_dia_habil
              ? 'bg-border-strong'
              : j.ok
                ? 'bg-pos'
                : 'bg-warn'
            return (
              <li key={j.job} className="flex items-baseline gap-3 py-2 text-xs">
                <span className={`h-1.5 w-1.5 shrink-0 self-center rounded-full ${punto}`} aria-hidden />
                <span className="num w-12 shrink-0 text-text-3">{j.hora_programada}</span>
                <span className="w-40 shrink-0 text-text-1">{NOMBRE_JOB[j.job] ?? j.job}</span>
                <span className={`min-w-0 flex-1 truncate ${op.es_dia_habil && !j.ok ? 'text-warn' : 'text-text-2'}`} title={j.detalle}>
                  {j.detalle}
                </span>
                <span className="num shrink-0 text-[10px] text-text-3" title={`última escritura de ${j.log}`}>
                  {j.log_modificado_utc ? fechaHoraChile(j.log_modificado_utc) : 'sin log'}
                </span>
              </li>
            )
          })}
        </ul>
      </Card>

      {/* salud de descarga sellada, últimos sellos */}
      <Card titulo="Salud de descarga sellada — últimos snapshots" className="capa-3">
        {op.descarga_semana.length > 0 ? (
          <ul className="divide-y divide-border text-xs">
            {op.descarga_semana.map((s) => {
              const completa = s.descarga_ok != null && s.descarga_ok === s.descarga_total
              return (
                <li key={s.fecha} className="flex items-baseline gap-3 py-1.5">
                  <span className="num w-24 shrink-0 text-text-2">{s.fecha}</span>
                  <span className="w-24 shrink-0 text-text-3">{s.origen}</span>
                  {s.descarga_ok == null ? (
                    <span className="text-text-3">sello pre-5.0 — sin dato de salud</span>
                  ) : (
                    <>
                      <span className={`num ${completa ? 'text-text-1' : 'text-warn'}`}>
                        {s.descarga_ok}/{s.descarga_total}
                      </span>
                      {!completa && (
                        <span className="min-w-0 truncate text-text-3" title={s.descarga_caidos ?? ''}>
                          caídos: {s.descarga_caidos}
                        </span>
                      )}
                    </>
                  )}
                </li>
              )
            })}
          </ul>
        ) : (
          <EmptyState
            titulo="Sin snapshots registrados"
            detalle="El primero se sella a las 18:15 de un día hábil."
          />
        )}
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* verificaciones */}
        <Card titulo="Verificaciones" className="capa-3">
          <ul className="divide-y divide-border text-xs">
            {op.verificaciones.estados.map((e) => (
              <li key={e.Estado} className="flex justify-between py-1.5">
                <span className="text-text-2">{e.Estado}</span>
                <span className="num text-text-1">{e.N}</span>
              </li>
            ))}
          </ul>
          {op.verificaciones.atascadas.length > 0 && (
            <div className="mt-3 border-t border-border pt-2">
              <p className="mb-1 text-[11px] font-medium text-text-2">
                Atascadas → sin_datos_mercado (terminal, fuera de métricas)
              </p>
              {op.verificaciones.atascadas.map((a) => (
                <p key={`${a.fecha}-${a.ticker}`} className="num text-[11px] text-text-3">
                  {a.fecha} · {a.ticker} · sesión {a.sesion_objetivo} ({a.exchange}) — la
                  fuente nunca publicó esa sesión
                </p>
              ))}
            </div>
          )}
          {op.verificaciones.pendientes.length > 0 && (
            <p className="mt-2 border-t border-border pt-2 text-[11px] text-text-3">
              {op.verificaciones.pendientes.length} pendientes madurando — la más
              próxima espera la sesión{' '}
              <span className="num">{op.verificaciones.pendientes[op.verificaciones.pendientes.length - 1].sesion_objetivo}</span>
            </p>
          )}
        </Card>

        {/* presupuesto IA */}
        <Card titulo="Presupuesto de IA (noticias)" className="capa-3">
          <div className="mb-2 flex items-baseline justify-between text-xs">
            <span className="text-text-2">
              gastado hoy <span className="num text-text-1">${pres.gasto_usd.toFixed(4)}</span>
            </span>
            <span className="num text-text-3">tope ${pres.tope_usd.toFixed(2)}</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-bg-3">
            <div
              className={`h-full ${pres.agotado ? 'bg-warn' : 'bg-cyan-dim'}`}
              style={{ width: `${Math.min(100, (pres.gasto_usd / pres.tope_usd) * 100)}%` }}
            />
          </div>
          <p className="mt-2 text-[11px] text-text-3">
            Freno duro entre lotes: al tope, el análisis se detiene y avisa por
            Telegram. Acumulado del mes: ${pres.gasto_mes_usd.toFixed(2)}.
          </p>
          {pres.corridas_hoy.length > 0 ? (
            <ul className="mt-2 divide-y divide-border border-t border-border text-[11px]">
              {pres.corridas_hoy.map((c, i) => (
                <li key={i} className="flex justify-between py-1.5">
                  <span className="text-text-2">
                    {String(c.origen)} · {String(c.resultado ?? '—')}
                    {c.analizados != null && ` · ${c.analizados} analizados`}
                  </span>
                  <span className="num text-text-1">${Number(c.costo_usd ?? 0).toFixed(4)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 border-t border-border pt-2 text-[11px] text-text-3">
              Sin corridas de IA registradas hoy — el job corre a las 17:50 en
              días hábiles.
            </p>
          )}
        </Card>
      </div>
    </div>
  )
}
