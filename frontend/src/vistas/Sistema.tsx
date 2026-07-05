import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { RegimeChip } from '../componentes/RegimeChip'
import { SignalBadge } from '../componentes/SignalBadge'
import { DataTable } from '../componentes/DataTable'
import { EmptyState, Cargando, ErrorCarga } from '../componentes/EmptyState'
import { CandleChart, type Vela } from '../componentes/CandleChart'
import { CorrHeatmap } from '../componentes/CorrHeatmap'
import { NewsSentiment } from '../componentes/NewsSentiment'

// ============================================================
// /sistema — catálogo del sistema de diseño (vista oculta).
// Cada componente base con datos de ejemplo y la regla que lo gobierna.
// Presupuesto de cian, jerarquía por fondos, números monoespaciados,
// incertidumbre de primera clase. NO hay enlace a esta vista en la nav.
// ============================================================

const velasEjemplo: Vela[] = Array.from({ length: 60 }, (_, i) => {
  const base = 100 + Math.sin(i / 6) * 8 + i * 0.3
  const o = base + (i % 3) - 1
  const c = base + ((i + 1) % 4) - 1.5
  return {
    t: new Date(Date.UTC(2026, 3, 1 + i)).toISOString().slice(0, 10),
    o,
    c,
    h: Math.max(o, c) + 1.2,
    l: Math.min(o, c) - 1.4,
    v: 1_000_000 + (i % 7) * 300_000,
  }
})

const filasEjemplo = [
  { ticker: '000660.KS', nombre: 'SK Hynix', est: -4.88, int80: 6.99, n: 120 },
  { ticker: '2330.TW', nombre: 'TSMC (Taiwán)', est: -3.1, int80: 4.2, n: 120 },
  { ticker: '8035.T', nombre: 'Tokyo Electron', est: -2.4, int80: 5.1, n: 118 },
]

export function Sistema() {
  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      <h1 className="font-display text-lg font-semibold text-text-1">
        Sistema de diseño
      </h1>
      <p className="text-xs text-text-3">
        Catálogo interno (sin enlace en la navegación). Reglas: jerarquía por
        niveles de fondo y bordes — nunca glow; máx 4 usos de cian por vista;
        toda cifra en monoespaciada tabular; la incertidumbre acompaña al
        número, jamás a un tooltip.
      </p>

      <Card titulo="RegimeChip">
        <div className="flex gap-3">
          <RegimeChip etiqueta="Alcista · vol alta" />
          <RegimeChip etiqueta={null} />
        </div>
      </Card>

      <Card titulo="StatTile — cifra con incertidumbre al lado">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          <StatTile etiqueta="Roca→Chip" valor={46} detalle="percentil 1 año" />
          <StatTile
            etiqueta="SOX último"
            valor="-5.44"
            sufijo="%"
            tono="neg"
            detalle="cierre 02 jul"
          />
          <StatTile
            etiqueta="Apertura estimada"
            valor="+1.20"
            sufijo="%"
            tono="pos"
            detalle="±2.4 pp · n=120 · R²=0.28"
          />
          <StatTile
            etiqueta="Track record"
            valor="0/5"
            detalle="en maduración — 1ª verificación posible 06 jul"
          />
        </div>
      </Card>

      <Card titulo="SignalBadge — el pie de emisión es obligatorio">
        <div className="grid gap-3 sm:grid-cols-2">
          <SignalBadge
            titulo="Apertura estimada: SK Hynix −4.88%"
            direccion="neg"
            magnitud="−4.88% ± 6.99 pp"
            porque="Beta de contagio 0.90 sobre el último movimiento real del SOX."
            nMuestra={120}
            r2={0.28}
            emitidaUtc="2026-07-04T10:06:05+00:00"
          />
          <SignalBadge
            titulo="Divergencia: SK Hynix vs Micron"
            direccion="neutra"
            magnitud="+9.3 pp spread 20d (z=+2.4)"
            porque="SK Hynix le saca 9.3 pp de rendimiento propio 20d a Micron (limpiado de índice local y moneda)."
          />
        </div>
      </Card>

      <Card titulo="DataTable — densa, números a la derecha">
        <DataTable
          columnas={[
            { clave: 'ticker', titulo: 'Ticker', render: (f) => <span className="num text-text-1">{f.ticker}</span> },
            { clave: 'nombre', titulo: 'Nombre', render: (f) => f.nombre },
            {
              clave: 'est',
              titulo: 'Estimado %',
              alinear: 'der',
              render: (f) => (
                <span className={f.est >= 0 ? 'text-pos' : 'text-neg'}>
                  {f.est >= 0 ? '+' : ''}
                  {f.est.toFixed(2)}
                </span>
              ),
            },
            { clave: 'int80', titulo: '±80%', alinear: 'der', render: (f) => `${f.int80.toFixed(1)} pp` },
            { clave: 'n', titulo: 'n', alinear: 'der', render: (f) => f.n },
          ]}
          filas={filasEjemplo}
          clavePor={(f) => f.ticker}
        />
      </Card>

      <Card titulo="CandleChart — lightweight-charts (TradingView)">
        <CandleChart velas={velasEjemplo} alto={260} />
      </Card>

      <Card titulo="CorrHeatmap">
        <CorrHeatmap
          columnas={['lag 5d', 'lag 10d', 'lag 20d']}
          filas={[
            { nombre: 'Demanda final → Fabricación', valores: [0.42, 0.31, 0.18] },
            { nombre: 'Fabricación → Equipos', valores: [0.28, 0.22, null] },
            { nombre: 'Equipos → Materiales', valores: [-0.12, 0.05, 0.09] },
          ]}
        />
      </Card>

      <Card titulo="NewsSentiment — texto plano, sin promoción">
        <NewsSentiment
          titulares={[
            {
              titular: 'SK Hynix amplía capacidad HBM ante demanda de aceleradores',
              fuente: 'Reuters',
              fecha: '2026-07-04',
              sentimiento: 0.62,
              tickers: '000660.KS',
            },
            {
              titular: 'Envíos de wafers caen por segundo trimestre consecutivo',
              fuente: 'SEMI',
              fecha: '2026-07-03',
              sentimiento: -0.41,
              tickers: '4063.T,3436.T',
            },
          ]}
        />
      </Card>

      <Card titulo="Estados: vacío honesto, carga (pulso, no shimmer), error">
        <div className="grid gap-3 sm:grid-cols-3">
          <EmptyState
            titulo="Track record en maduración: 0/5"
            detalle="Primera verificación posible: 06 jul (apertura de Seúl)."
          />
          <Cargando alto="h-28" />
          <ErrorCarga mensaje="No se pudo leer /api/hoy: la API no responde en :8000." />
        </div>
      </Card>
    </div>
  )
}
