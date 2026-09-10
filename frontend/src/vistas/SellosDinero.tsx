import { useEffect, useState } from 'react'
import { useApi } from '../lib/api'
import type { DatosSellosDinero } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { Estatus } from '../componentes/CifraConIntervalo'
import { ErrorCarga, EsqueletoCard } from '../componentes/EmptyState'

// ============================================================
// /sellos — lo que la regla dimensionó sobre un sorteo sin información para la próxima apertura (E0) y el
// estado de la cuenta de práctica (E1). Corrida 12, bloque 5.
//
// Es la parte visible de la visión y por eso es donde más fácil es mentir.
// Regla del bloque: cada número lleva estatus, n donde exista y fuente. Las
// frases fijas de esta vista pasaron por el curador-epistemico. Ninguna
// sugiere que exista una ventaja o un resultado: no lo hay.
//
// Actualización: sondeo corto (60 s) con el mismo useApi; la cuenta
// regresiva corre en el navegador desde `apertura_objetivo_utc`. Sin
// dependencia nueva.
// ============================================================

const SONDEO_MS = 60 * 1000
const CHILE = 'America/Santiago'

function horaChile(iso: string | null | undefined) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('es-CL', { timeZone: CHILE, hour12: false })
}

function CuentaRegresiva({ hasta }: { hasta: string | null | undefined }) {
  const [ahora, setAhora] = useState(() => Date.now())
  useEffect(() => {
    const t = setInterval(() => setAhora(Date.now()), 1000)
    return () => clearInterval(t)
  }, [])
  if (!hasta) return <span className="text-text-3">sin apertura objetivo</span>
  const ms = new Date(hasta).getTime() - ahora
  if (ms <= 0) return <span className="text-text-2">la apertura objetivo ya pasó</span>
  const s = Math.floor(ms / 1000)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const ss = s % 60
  return (
    <span className="font-mono tabular-nums text-text-1">
      {String(h).padStart(2, '0')}:{String(m).padStart(2, '0')}:{String(ss).padStart(2, '0')}
    </span>
  )
}

export function SellosDinero() {
  const { data, isLoading, error, refetch } = useApi<DatosSellosDinero>('/dinero/sellos', {
    refrescoMs: SONDEO_MS,
  })
  if (isLoading) return <EsqueletoCard alto="h-96" />
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos
  const u = d.ultimo_sello
  const compras = d.decisiones_proxima_apertura.filter((f) => f.decision !== 'nada')
  const nada = d.decisiones_proxima_apertura.filter((f) => f.decision === 'nada')

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      <Card className="capa-1 border-acento-2" estatus={d.estatus}>
        <div className="mb-2 flex flex-wrap items-baseline gap-3">
          <h2 className="font-display text-[15px] font-semibold text-text-1">
            Riel de dinero — lo sellado para la próxima apertura
          </h2>
          <Estatus valor="SIMULADO" />
          <span className="font-mono text-[11px] text-text-2">tamaño nominal: cero</span>
        </div>
        <p className="max-w-3xl text-xs leading-relaxed text-text-2">{d.que_es}</p>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-2">
          <span className="text-text-1">Qué señal se sella:</span> {d.senal_fuente}.
        </p>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-3">
          {d.smh} (censo de 1 día, fuente: dinero/resultados/universo_operable.json)
        </p>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card titulo="E0 — sesiones selladas prospectivas" estatus={d.E0.estatus} className="capa-1">
          <div className="grid gap-3 sm:grid-cols-4">
            {[
              ['Sesiones que cuentan para N', `${d.E0.sesiones_que_cuentan_para_N}`, d.E0.fuente_conteos],
              ['N que cierra E0', `${d.E0.N_objetivo}`, d.E0.N_objetivo_fuente],
              ['Sesiones selladas (todas)', `${d.E0.sesiones_selladas}`, d.E0.fuente_conteos],
              ['Filas (una por instrumento)', `${d.E0.filas}`, d.E0.fuente_conteos],
            ].map(([k, v, fuente]) => (
              <div key={k} className="rounded border border-border bg-bg-2 px-3 py-2">
                <div className="mini-label text-text-3">{k}</div>
                <div className="mt-1 font-mono text-[18px] tabular-nums text-text-1">{v}</div>
                <div className="mt-0.5 text-[10px] text-text-3">fuente: {fuente}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 max-w-3xl text-[11px] leading-relaxed text-text-2">{d.E0.nota}</p>
        </Card>

        <Card titulo="E1 — cuenta de práctica" estatus={d.E1.estatus} className="capa-1">
          <div className="mb-2 flex flex-wrap items-baseline gap-2">
            <span className="font-mono text-[12px] text-text-1">{d.E1.estado}</span>
            <span className="font-mono text-[11px] text-text-2">cuenta: {d.E1.etiqueta.toLowerCase()}</span>
          </div>
          {d.E1.cuenta_practica == null ? (
            <div className="rounded border border-border bg-bg-2 px-3 py-2 text-[12px] leading-relaxed text-text-2">
              <span className="text-text-1">No hay cuenta de práctica conectada.</span> {d.E1.por_que}.
              Esta tarjeta no muestra posiciones, efectivo ni ejecuciones porque no existen; se
              llenará con lo leído por API, con su marca de retraso, cuando E1 corra.
              <div className="mt-1 font-mono text-[10px] text-text-3">{d.E1.adaptador}</div>
            </div>
          ) : (
            <div className="text-[12px] text-text-2">
              Cuenta {d.E1.cuenta_practica} · retraso declarado{' '}
              {d.E1.marca_retraso?.retraso_min ?? '?'} min ({d.E1.marca_retraso?.descripcion ?? '?'}).
            </div>
          )}
        </Card>
      </div>

      <Card titulo="Último sello y su apertura objetivo" estatus={d.estatus} className="capa-1">
        {!u ? (
          <p className="text-[12px] text-text-2">
            Todavía no hay ningún sello. La primera fila existirá cuando corra{' '}
            <span className="font-mono">python -m dinero.sello_dinero --sellar</span> fuera de la ventana
            17:50 a 20:30 de producción y antes de la apertura objetivo.
          </p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ['Emitida (hora de Chile)', horaChile(u.timestamp_utc)],
              ['Insumo conocible desde', horaChile(u.available_at)],
              ['Apertura objetivo (Chile)', `${u.sesion_objetivo} · ${horaChile(u.apertura_objetivo_utc)}`],
              ['Estado de la fila', `${u.estado}${u.cuenta_para_N ? ' · cuenta para N' : ' · no cuenta para N'}`],
            ].map(([k, v]) => (
              <div key={k} className="rounded border border-border bg-bg-2 px-3 py-2">
                <div className="mini-label text-text-3">{k}</div>
                <div className="mt-1 font-mono text-[12px] tabular-nums text-text-1">{v}</div>
              </div>
            ))}
            <div className="rounded border border-border bg-bg-2 px-3 py-2 sm:col-span-2">
              <div className="mini-label text-text-3">Falta para la apertura objetivo</div>
              <div className="mt-1 text-[18px]">
                <CuentaRegresiva hasta={u.apertura_objetivo_utc} />
              </div>
              <div className="mt-0.5 text-[10px] text-text-3">
                computado en el navegador desde apertura_objetivo_utc; a esa hora no ocurre nada: el tamaño
                sellado es cero
              </div>
            </div>
            <div className="rounded border border-border bg-bg-2 px-3 py-2 sm:col-span-2">
              <div className="mini-label text-text-3">Insumo sellado</div>
              <div className="mt-1 font-mono text-[10px] text-text-2">
                base {u.insumo_base_sha256?.slice(0, 16)}… · extensión {u.insumo_ext_sha256?.slice(0, 16)}… ·
                plataforma {u.plataforma_version} · juego {u.juego} · presupuesto declarado{' '}
                {u.presupuesto_usd.toFixed(0)} USD
              </div>
            </div>
          </div>
        )}
      </Card>

      {u && (
        <Card
          titulo={`Decisiones selladas para la apertura del ${u.sesion_objetivo} — señal sin información, tamaño nominal cero`}
          estatus={d.estatus}
          className="capa-1"
        >
          <p className="mb-3 max-w-3xl text-[11px] leading-relaxed text-text-2">
            {compras.length} de {d.decisiones_proxima_apertura.length} instrumentos operables tienen una
            decisión distinta de «nada». La columna «acciones por la regla» es lo que el juego{' '}
            {u.juego} dimensionaría con {u.presupuesto_usd.toFixed(0)} USD; lo sellado es tamaño cero. La
            señal es un sorteo sin información: la magnitud y su banda se muestran para que se pueda
            auditar la decisión, no porque signifiquen algo sobre el precio.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="border-b border-border text-left text-[10px] uppercase tracking-wide text-text-3">
                  <th className="py-1 pr-3">Instrumento</th>
                  <th className="py-1 pr-3">Decisión</th>
                  <th className="py-1 pr-3 text-right">Acciones por la regla</th>
                  <th className="py-1 pr-3 text-right">Tamaño sellado</th>
                  <th className="py-1 pr-3 text-right">Precio ref. USD (cierre del insumo sellado)</th>
                  <th className="py-1 pr-3 text-right">Señal pp [banda del sorteo]</th>
                  <th className="py-1">Motivo</th>
                </tr>
              </thead>
              <tbody>
                {[...compras, ...nada].map((f) => (
                  <tr key={f.ticker} className="border-b border-border/50">
                    <td className="py-1 pr-3 font-mono text-text-1">{f.ticker}</td>
                    <td className="py-1 pr-3 text-text-1">{f.decision}</td>
                    <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-2">
                      {f.acciones_regla ?? '—'}
                    </td>
                    <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-1">
                      {f.tamano_nominal}
                    </td>
                    <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-2">
                      {f.precio_ref_usd?.toFixed(2) ?? '—'}
                    </td>
                    <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-2">
                      {f.senal_magnitud_pp != null
                        ? `${f.senal_magnitud_pp.toFixed(2)} [${f.senal_banda_baja_pp?.toFixed(1)}, ${f.senal_banda_alta_pp?.toFixed(1)}]`
                        : '—'}
                    </td>
                    <td className="py-1 text-[11px] text-text-3">{f.motivo ?? ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Card
        titulo="Gate de invariancia de la cuenta en papel v2 (corrida 11), no de E0"
        estatus={d.gate_invariancia_ultima_corrida.estatus}
        className="capa-1"
      >
        <p className="mb-2 max-w-3xl text-[11px] leading-relaxed text-text-2">
          {d.gate_invariancia_ultima_corrida.nota_e0}
        </p>
        <div className="flex flex-wrap items-baseline gap-3 text-[11px]">
          <span className="font-mono text-text-1">{d.gate_invariancia_ultima_corrida.resultado ?? 'sin gate'}</span>
          <span className="font-mono tabular-nums text-text-2">
            {d.gate_invariancia_ultima_corrida.cortes} cortes · {d.gate_invariancia_ultima_corrida.fecha ?? '—'}
          </span>
        </div>
        <p className="mt-2 max-w-3xl text-[11px] leading-relaxed text-text-2">
          {d.gate_invariancia_ultima_corrida.alcance}
        </p>
        <div className="mt-1 font-mono text-[10px] text-text-3">
          fuente: {d.gate_invariancia_ultima_corrida.fuente}
        </div>
      </Card>
    </div>
  )
}
