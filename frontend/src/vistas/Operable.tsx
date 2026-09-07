import { useApi } from '../lib/api'
import type { DatosUniversoOperable, EslabonOperable } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { Estatus } from '../componentes/CifraConIntervalo'
import { ErrorCarga, EsqueletoCard } from '../componentes/EmptyState'

// ============================================================
// /operable — la cadena, hecha visible: qué eslabón se puede comprar de
// verdad desde Chile con el presupuesto declarado, y qué eslabón no.
//
// Es el mapa de `docs/universo_operable.md` en pantalla. No agrega ni una
// cifra: todo viene de /api/dinero/universo, que a su vez sirve el JSON
// que genera `python -m dinero.mapa` desde los precios congelados.
//
// Regla de esta vista: los HUECOS se muestran, no se tapan. Un eslabón
// cuyo dominante no se puede comprar dice que no se puede comprar, y dice
// a quién se le compra en su lugar y en qué se diferencia.
// ============================================================

const COLOR_ESTADO: Record<string, string> = {
  REPRESENTADO: 'text-text-1',
  SUSTITUIDO: 'text-acento-2',
  HUECO: 'text-neg',
}

function Eslabon({ e }: { e: EslabonOperable }) {
  const difieren = e.estado !== e.estado_exigiendo_liquidez
  return (
    <Card className="capa-1">
      <div className="mb-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h3 className="font-display text-[14px] font-semibold text-text-1">{e.nombre}</h3>
        <span className={`font-mono text-[11px] uppercase tracking-wide ${COLOR_ESTADO[e.estado]}`}>
          {e.estado}
        </span>
        {difieren && (
          <span className="text-[11px] text-text-2">
            — exigiendo liquidez verificada:{' '}
            <span className={`font-mono ${COLOR_ESTADO[e.estado_exigiendo_liquidez]}`}>
              {e.estado_exigiendo_liquidez}
            </span>
          </span>
        )}
      </div>
      <p className="mb-1 text-[11px] leading-relaxed text-text-2">
        <span className="mini-label text-text-3">Quién domina</span>{' '}
        <span className="rounded border border-border px-1 text-[10px] uppercase text-text-3">
          contexto no verificado
        </span>{' '}
        {e.dominante_contexto_no_verificado}
      </p>
      <p className="mb-3 text-[11px] leading-relaxed text-text-2">
        <span className="mini-label text-text-3">Obstáculo</span> {e.obstaculo}
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-[12px]">
          <thead>
            <tr className="border-b border-border text-left text-[10px] uppercase tracking-wide text-text-3">
              <th className="py-1 pr-3">Ticker</th>
              <th className="py-1 pr-3">Instrumento</th>
              <th className="py-1 pr-3">Forma</th>
              <th className="py-1 pr-3">Rol</th>
              <th className="py-1 pr-3 text-right">Cierre USD</th>
              <th className="py-1 pr-3 text-right">Con 500 USD</th>
              <th className="py-1 text-right">Comisión 1 acción</th>
            </tr>
          </thead>
          <tbody>
            {e.instrumentos.map((i) => (
              <tr key={i.ticker} className="border-b border-border/50">
                <td className="py-1 pr-3 font-mono text-text-1">{i.ticker}</td>
                <td className="py-1 pr-3 text-text-2">
                  {i.nombre}
                  {i.liquidez_no_verificada && (
                    <span className="ml-1 rounded border border-border px-1 text-[9px] uppercase text-text-3">
                      liquidez no verificada
                    </span>
                  )}
                </td>
                <td className="py-1 pr-3 text-text-3">{i.forma}</td>
                <td className="py-1 pr-3 text-text-3">{i.rol}</td>
                <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-1">
                  {i.precio_usd == null ? 'no verificado' : i.precio_usd.toFixed(2)}
                </td>
                <td className="py-1 pr-3 text-right font-mono tabular-nums">
                  {i.alcanza_con_techo ? (
                    <span className="text-text-1">{i.acciones_con_techo}</span>
                  ) : (
                    <span className="text-neg">no alcanza</span>
                  )}
                </td>
                <td className="py-1 text-right font-mono tabular-nums text-text-2">
                  {i.comision_orden_minima_pct == null
                    ? '—'
                    : `${i.comision_orden_minima_pct.toFixed(2)} %`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {e.instrumentos.some((i) => i.sustituye_a) && (
        <ul className="mt-3 grid gap-1 text-[11px] leading-relaxed text-text-2">
          {e.instrumentos
            .filter((i) => i.sustituye_a)
            .map((i) => (
              <li key={i.ticker}>
                <span className="font-mono text-text-1">{i.ticker}</span> sustituye a{' '}
                {i.sustituye_a}. {i.diferencia}
              </li>
            ))}
        </ul>
      )}

      {e.huecos.length > 0 && (
        <div className="mt-3 rounded border border-border bg-bg-2 p-3">
          <div className="mini-label mb-1 text-text-3">
            Huecos declarados — no se tapan con un sustituto
          </div>
          <ul className="grid gap-1 text-[11px] leading-relaxed text-text-2">
            {e.huecos.map((h) => (
              <li key={h.quien}>
                <span className="text-text-1">{h.quien}</span> — {h.clase}. {h.por_que}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  )
}

export function Operable() {
  const { data, isLoading, error, refetch } = useApi<DatosUniversoOperable>(
    '/dinero/universo',
  )
  if (isLoading) return <EsqueletoCard alto="h-96" />
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos
  const r = d.resumen

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      <Card className="capa-1">
        <div className="mb-2 flex flex-wrap items-baseline gap-3">
          <h2 className="font-display text-[15px] font-semibold text-text-1">
            La cadena, y qué parte de ella se puede comprar
          </h2>
          <Estatus valor={d.estatus} />
        </div>
        <p className="mb-3 max-w-3xl text-xs leading-relaxed text-text-2">
          El mapa del <span className="text-text-1">riel de dinero</span>: qué eslabón de la
          cadena de semiconductores se puede comprar desde Chile con{' '}
          {d.presupuesto.piso_usd.toFixed(0)} a {d.presupuesto.techo_usd.toFixed(0)} dólares,
          y cuál no. No es una recomendación de compra y no hay cuenta de corredora abierta.
        </p>
        {d.estatus_de_los_precios && (
          <p className="mb-3 max-w-3xl text-[11px] leading-relaxed text-text-3">
            El rótulo de arriba es el del mapa como objeto del riel de dinero. Los precios
            que lo sostienen tienen su propio estatus:{' '}
            <span className="text-text-2">{d.estatus_de_los_precios}</span>. El censo es de
            un solo día: los casos al borde del presupuesto están declarados en{' '}
            <span className="font-mono text-[10px]">docs/universo_operable.md</span>.
          </p>
        )}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Candidatos verificados', `${r.verificados} de ${r.candidatos}`],
            ['Eslabones representados', `${r.representados} de 8`],
            ['Sustituidos', `${r.sustituidos}`],
            ['Huecos', `${r.huecos}`],
          ].map(([k, v]) => (
            <div key={k} className="rounded border border-border bg-bg-2 px-3 py-2">
              <div className="mini-label text-text-3">{k}</div>
              <div className="mt-1 font-mono text-[18px] tabular-nums text-text-1">{v}</div>
            </div>
          ))}
        </div>
        <p className="mt-3 max-w-3xl text-[11px] leading-relaxed text-text-2">
          Exigiendo además que el instrumento tenga <span className="text-text-1">liquidez
          verificada</span> —que esta corrida no verificó para los ADR de mostrador— quedan{' '}
          <span className="font-mono">{r.representados_exigiendo_liquidez}</span> representados,{' '}
          <span className="font-mono">{r.sustituidos_exigiendo_liquidez}</span> sustituidos y{' '}
          <span className="font-mono">{r.huecos_exigiendo_liquidez}</span> huecos. «Representado»
          significa <span className="text-text-1">un dominante comprable con el techo del
          presupuesto</span>, no un dominante listado: uno que cotiza pero cuya acción cuesta más
          de lo que hay no representa nada.
        </p>
        <p className="mt-2 max-w-3xl text-[11px] leading-relaxed text-text-3">
          Precios de {d.fuente.archivo} — {d.fuente.filas} filas, {d.fuente.desde} a{' '}
          {d.fuente.hasta}. La comisión es un supuesto declarado, no un arancel leído: no hay
          cuenta abierta y por lo tanto no hay tarifario.
        </p>
      </Card>

      {d.eslabones.map((e) => (
        <Eslabon key={e.clave} e={e} />
      ))}
    </div>
  )
}
