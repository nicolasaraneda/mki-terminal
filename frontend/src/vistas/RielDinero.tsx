import { useApi } from '../lib/api'
import type { DatosCuentaPapel } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { CifraConIntervalo, Estatus } from '../componentes/CifraConIntervalo'
import { ErrorCarga, EsqueletoCard } from '../componentes/EmptyState'

// ============================================================
// /dinero — la cuenta en papel contra la línea base.
//
// La etiqueta SIMULADO va en el primer bloque de la vista, visible sin
// hacer scroll: es la primera cosa que alguien tiene que saber antes de
// leer un solo número de esta pantalla.
//
// Y la advertencia que importa más que la etiqueta: la señal que alimenta
// esta cuenta NO TIENE INFORMACIÓN. Lo que se mide es fricción. Ninguna de
// estas cifras es evidencia de habilidad, y la vista lo dice con palabras
// además de con rótulos.
// ============================================================

const DESLIZAMIENTO_MOSTRADO = 5

export function RielDinero() {
  const { data, isLoading, error, refetch } = useApi<DatosCuentaPapel>('/dinero/cuenta')
  if (isLoading) return <EsqueletoCard alto="h-96" />
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos

  const base = d.linea_base.filter((f) => f.deslizamiento_pb === DESLIZAMIENTO_MOSTRADO)
  const juegos = d.juegos.filter((f) => f.deslizamiento_pb === DESLIZAMIENTO_MOSTRADO)
  const fp = d.falsos_positivos

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* La etiqueta, arriba de todo y sin scroll. */}
      <Card className="capa-1 border-acento-2">
        <div className="mb-2 flex flex-wrap items-baseline gap-3">
          <h2 className="font-display text-[15px] font-semibold text-text-1">
            Riel de dinero — cuenta en papel
          </h2>
          <Estatus valor="SIMULADO" />
          <Estatus valor={d.estatus} />
        </div>
        {d.retirado && (
          <div className="mb-3 rounded border border-acento-2 bg-bg-2 px-3 py-2">
            <div className="mini-label text-text-1">
              Cifras retiradas el {d.retirado.fecha}
            </div>
            <p className="mt-1 max-w-3xl text-xs leading-relaxed text-text-2">
              <span className="text-text-1">
                Ninguna cifra de esta pantalla se puede citar.
              </span>{' '}
              {d.retirado.causa}
            </p>
            <p className="mt-1 max-w-3xl text-xs leading-relaxed text-text-2">
              {d.retirado.consecuencia} Fuente del retiro:{' '}
              <span className="font-mono text-[11px]">{d.retirado.fuente}</span>.
            </p>
            <p className="mt-1 max-w-3xl text-xs leading-relaxed text-text-3">
              Lo que sigue se deja a la vista, sin reescribir, para que se pueda auditar
              contra la versión corregida cuando exista.
            </p>
          </div>
        )}
        <p className="max-w-3xl text-xs leading-relaxed text-text-2">
          <span className="text-text-1">Nada de esta pantalla movió un peso.</span> No hay
          cuenta de corredora, no se envió ninguna orden y ninguna cifra de acá entra al
          README ni sostiene ninguna afirmación del proyecto.
        </p>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-2">
          Y lo que más importa: <span className="text-text-1">la señal que alimenta esta
          cuenta no tiene información</span>. Se sorteó de la distribución histórica de
          retornos, sin relación con lo que pasa después. Lo que se mide acá es{' '}
          <span className="text-text-1">fricción</span>, no habilidad. Una estrategia con
          señal de verdad tendría que superar esto antes de poder llamarse otra cosa.
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          {[
            ['Capital aportado', `${d.aportado_usd.toFixed(0)} USD`],
            ['Ventana', `${d.ventana.desde} → ${d.ventana.hasta}`],
            ['Instrumentos operables', `${d.instrumentos_operables}`],
          ].map(([k, v]) => (
            <div key={k} className="rounded border border-border bg-bg-2 px-3 py-2">
              <div className="mini-label text-text-3">{k}</div>
              <div className="mt-1 font-mono text-[13px] tabular-nums text-text-1">{v}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card titulo="La comisión se come el capital — el hallazgo robusto" className="capa-1">
        <p className="mb-3 max-w-3xl text-[11px] leading-relaxed text-text-2">
          Depende sobre todo de cuántas órdenes emite cada juego, y el número de órdenes
          depende del sorteo: por eso la banda entre semillas va debajo de la tabla. Con el
          mínimo por orden del arancel vigente (
          {d.reconstruccion?.costo?.comision_minima_usd ?? '?'} USD) y{' '}
          {d.aportado_usd.toFixed(0)} dólares de capital, rotar la cartera cuesta esto:
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-border text-left text-[10px] uppercase tracking-wide text-text-3">
                <th className="py-1 pr-3">Juego</th>
                <th className="py-1 pr-3 text-right">Órdenes</th>
                <th className="py-1 pr-3 text-right">Comisiones USD</th>
                <th className="py-1 text-right">Fracción del capital</th>
              </tr>
            </thead>
            <tbody>
              {[...juegos, ...base].map((f) => (
                <tr key={f.juego ?? f.etf} className="border-b border-border/50">
                  <td className="py-1 pr-3 text-text-1">
                    {f.juego ?? `línea base ${f.etf}`}
                  </td>
                  <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-2">
                    {f.ordenes}
                  </td>
                  <td className="py-1 pr-3 text-right font-mono tabular-nums text-text-2">
                    {f.comisiones_usd.toFixed(2)}
                  </td>
                  <td className="py-1 text-right font-mono tabular-nums text-text-1">
                    {((100 * f.comisiones_usd) / f.aportado_usd).toFixed(1)} %
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {d.barrido_semillas && (
          <p className="mt-3 max-w-3xl text-[11px] leading-relaxed text-text-2">
            <span className="text-text-1">
              Con {d.barrido_semillas.K} semillas del sorteo (deslizamiento{' '}
              {d.barrido_semillas.deslizamiento_pb} pb):
            </span>{' '}
            {Object.entries(d.barrido_semillas.comisiones_pct_del_aportado).map(([j, x]) => (
              <span key={j} className="mr-3 font-mono text-[11px] tabular-nums">
                {j} {x.mediana.toFixed(1)} % [{x.banda_p2_5_p97_5[0].toFixed(1)},{' '}
                {x.banda_p2_5_p97_5[1].toFixed(1)}]
              </span>
            ))}
            . La tabla de arriba es la semilla de la página; la banda es percentiles 2,5 y 97,5
            entre semillas, no un intervalo de cobertura nominal.
          </p>
        )}
      </Card>

      <Card
        titulo={`Contra la línea base — deslizamiento ${DESLIZAMIENTO_MOSTRADO} pb por lado`}
        className="capa-1"
      >
        <p className="mb-3 max-w-3xl text-[11px] leading-relaxed text-text-2">
          Diferencia de retorno semanal medio contra cada línea base, con intervalo de
          bootstrap circular de bloques sobre semanas. Los tres juegos se muestran{' '}
          <span className="text-text-1">sin ranking y sin recomendación</span>: elegir uno
          mirando esta tabla sería elegir la vara después de ver el tiro. El que rige por
          defecto lo fija una regla escrita, no su resultado.
        </p>
        <div className="grid gap-3 lg:grid-cols-3">
          {juegos.map((f) =>
            Object.entries(f.contra ?? {}).map(([etf, c]) => (
              <CifraConIntervalo
                key={`${f.juego}-${etf}`}
                etiqueta={`${f.juego} vs ${etf}`}
                valor={c.dif_media_pp}
                intervalo={[c.ic_lo, c.ic_hi]}
                unidad="pp/semana"
                tipoIntervalo="IC95 de bloques"
                n={`${c.semanas} semanas`}
                decimales={3}
              />
            )),
          )}
        </div>
      </Card>

      <Card titulo="Por qué no hay que creerle a un intervalo de esta página — lectura corregida" className="capa-1">
        <div className="grid gap-3 lg:grid-cols-[auto_1fr] lg:items-center">
          <div className="rounded border border-border bg-bg-2 px-3 py-2">
            <div className="mini-label text-text-3">
              Comparaciones con intervalo que excluye el cero
            </div>
            <div className="mt-1 font-mono text-[22px] tabular-nums text-text-1">
              {fp.con_ic_que_excluye_cero} de {fp.comparaciones}
            </div>
            <div className="mt-0.5 font-mono text-[11px] tabular-nums text-text-2">
              {((100 * fp.con_ic_que_excluye_cero) / fp.comparaciones).toFixed(0)} %
            </div>
          </div>
          <p className="max-w-2xl text-[11px] leading-relaxed text-text-2">
            <span className="text-text-1">No es una tasa de falsos positivos.</span>{' '}
            {fp.nota}
          </p>
        </div>
      </Card>

      <Card titulo="El barrido de costo no es una curva de sensibilidad" className="capa-1">
        <p className="max-w-3xl text-[11px] leading-relaxed text-text-2">
          El barrido corre a {d.barrido_deslizamiento_pb.join(', ')} puntos básicos por lado.
          Las filas <span className="text-text-1">no son la misma estrategia a distinto
          costo</span>: el deslizamiento cambia cuántas acciones enteras entran en el margen,
          y eso cambia qué instrumento se compra. Con acciones enteras y{' '}
          {d.aportado_usd.toFixed(0)} dólares, el resultado lo decide cuál de los{' '}
          {d.instrumentos_operables} instrumentos tocó en el sorteo. Compararlas entre sí
          sería un error, y por eso esta vista muestra una sola pasada del barrido de costo; la
          variación entre sorteos está en la tarjeta de comisiones.
        </p>
      </Card>
    </div>
  )
}
