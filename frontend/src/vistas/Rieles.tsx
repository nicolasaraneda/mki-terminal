import { useApi } from '../lib/api'
import type { DatosRieles, Riel } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { CifraConIntervalo, Estatus } from '../componentes/CifraConIntervalo'
import { ErrorCarga, EsqueletoCard } from '../componentes/EmptyState'

// ============================================================
// /rieles — el proyecto entero de un vistazo.
//
// Dos rieles, uno al lado del otro, con lo mismo declarado de cada uno:
// qué mide, en qué horizonte, contra qué vara, cuánta muestra lleva, qué
// le falta para veredicto y QUÉ LO MATA. Ese último campo es el que hace
// que esta vista no sea un tablero de logros.
//
// Ninguna cifra se escribe acá: el riel de medición se lee del árbitro
// (`cifras.sellada()`) a través de /api/rieles.
// ============================================================

function Campo({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <div className="border-t border-border/60 py-2">
      <div className="mini-label text-text-3">{k}</div>
      <div className="mt-0.5 text-[12px] leading-relaxed text-text-2">{children}</div>
    </div>
  )
}

function Columna({ r }: { r: Riel }) {
  return (
    <Card className="capa-1">
      <div className="mb-2 flex flex-wrap items-baseline gap-3">
        <h3 className="font-display text-[15px] font-semibold text-text-1">{r.nombre}</h3>
        <Estatus valor={r.estatus} />
        {!r.mueve_plata && (
          <span className="text-[11px] text-text-3">no mueve plata</span>
        )}
      </div>

      {r.cifras && (
        <div className="mb-3 grid gap-2 sm:grid-cols-2">
          {r.cifras.map((c) => (
            <CifraConIntervalo
              key={c.nombre}
              etiqueta={c.nombre}
              valor={c.valor_pct}
              intervalo={c.intervalo}
              unidad={c.nombre.includes('acierto') ? '%' : 'pp'}
              tipoIntervalo={c.tipo_intervalo}
              n={r.muestra.n as number}
              decimales={c.nombre.includes('MAE') ? 4 : 1}
            />
          ))}
        </div>
      )}

      {r.senal_larga && (
        <div className="mb-3 rounded border border-border bg-bg-2 px-3 py-2">
          <div className="mini-label text-text-3">Señal larga v1</div>
          <div className="mt-1 text-[12px] leading-relaxed text-text-2">
            {r.senal_larga.ganan_a_la_climatologia} de {r.senal_larga.celdas} celdas le ganan
            a la climatología causal, sobre {r.senal_larga.contrastes} contrastes.{' '}
            {r.senal_larga.L1_refutada && (
              <span className="text-text-1">
                L1 —el contagio directo, la forma simple de la hipótesis— queda REFUTADA por
                su propia regla pre-registrada.
              </span>
            )}
          </div>
        </div>
      )}

      {r.cuenta_en_papel && (
        <div className="mb-3 rounded border border-border bg-bg-2 px-3 py-2">
          <div className="mini-label text-text-3">Cuenta en papel</div>
          <div className="mt-1 text-[12px] leading-relaxed text-text-2">
            {r.cuenta_en_papel.aportado_usd.toFixed(0)} USD simulados.{' '}
            {r.cuenta_en_papel.falsos_positivos.con_ic_que_excluye_cero} de{' '}
            {r.cuenta_en_papel.falsos_positivos.comparaciones} comparaciones dan un intervalo
            que excluye el cero <span className="text-text-1">con una señal sin
            información</span>: todos falsos positivos por construcción.
          </div>
        </div>
      )}

      <Campo k="Qué mide">{r.que_mide}</Campo>
      <Campo k="Horizonte">{r.horizonte}</Campo>
      <Campo k="Contra qué vara">{r.vara}</Campo>
      <Campo k="Cuánta muestra lleva">
        <span className="font-mono tabular-nums">
          {Object.entries(r.muestra)
            .filter(([k]) => k !== 'nota')
            .map(([k, v]) => `${k} = ${v}`)
            .join(' · ')}
        </span>
        {r.muestra.nota && (
          <div className="mt-1 text-text-3">{String(r.muestra.nota)}</div>
        )}
        {r.n_efectivo != null && (
          <div className="mt-1 font-mono tabular-nums text-text-3">
            n efectivo = {r.n_efectivo} · ICC = {r.icc} · DEFF = {r.deff} — las filas no son
            independientes, y el n efectivo es el que manda.
          </div>
        )}
      </Campo>
      <Campo k="Qué le falta para veredicto">{r.falta_para_veredicto}</Campo>
      <Campo k="Qué lo mata">
        <span className="text-text-1">{r.que_lo_mata}</span>
      </Campo>
      {r.potencia && <Campo k="Potencia">{r.potencia.nota}</Campo>}
      {r.procedencia && (
        <Campo k="Procedencia de las cifras">
          <span className="font-mono text-[11px]">{r.procedencia}</span>
        </Campo>
      )}
    </Card>
  )
}

export function Rieles() {
  const { data, isLoading, error, refetch } = useApi<DatosRieles>('/rieles')
  if (isLoading) return <EsqueletoCard alto="h-96" />
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      <Card className="capa-1">
        <h2 className="mb-2 font-display text-[15px] font-semibold text-text-1">
          Los dos rieles
        </h2>
        <p className="max-w-3xl text-xs leading-relaxed text-text-2">{d.por_que_son_dos}</p>
        <p className="mt-2 max-w-3xl text-[11px] leading-relaxed text-text-3">
          Cada riel declara qué lo mata. Un tablero que sólo muestra lo que va bien no es un
          tablero: es publicidad.
        </p>
      </Card>
      <div className="grid gap-4 xl:grid-cols-2">
        {d.rieles.map((r) => (
          <Columna key={r.nombre} r={r} />
        ))}
      </div>
    </div>
  )
}
