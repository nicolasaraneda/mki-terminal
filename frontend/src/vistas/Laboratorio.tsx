import { useApi } from '../lib/api'
import type { DatosHistorial } from '../lib/tipos'
import { Card } from '../componentes/Card'
import { StatTile } from '../componentes/StatTile'
import { ErrorCarga, EsqueletoCard, EsqueletoTiles } from '../componentes/EmptyState'

// ============================================================
// /laboratorio — el rigor visible ANTES de que exista el resultado
// (Etapa 5.0 WS5). El motor de backtest B0→B5 está construido y probado;
// su ejecución con veredicto espera el gatillo congelado en el GATE B y
// la decisión humana. Esta vista muestra el diseño del experimento y el
// progreso hacia la madurez — jamás un resultado prematuro.
// ============================================================

const BASELINES = [
  { id: 'B0', nombre: 'Cartera equiponderada / señal nula', pregunta: '¿El período regaló retornos? Piso de MAE y cartera sin criterio.' },
  { id: 'B1', nombre: 'Momentum propio 20d', pregunta: '¿Basta la inercia propia, sin mirar el SOX?' },
  { id: 'B2', nombre: 'Contagio SOX(t−1) — el modelo de producción v4.6.0, congelado', pregunta: '¿El contagio agrega sobre la inercia? El backtest lo audita, no lo reinventa.' },
  { id: 'B3', nombre: 'Cuant de precio combinado', pregunta: '¿Combinar las señales de precio (beta, momentum, régimen, divergencias) mejora al contagio solo?' },
  { id: 'B4', nombre: 'B3 + eventos de noticias', pregunta: '¿El sentimiento y el buzz agregan algo que el precio no traía ya?' },
  { id: 'B5', nombre: 'B4 + cadena de valor', pregunta: '¿La tesis central (roca→chip anticipa) agrega valor marginal medible?' },
]

const OBJETIVO_N = 150
const FECHA_LIMITE = '2026-10-25' // 3 meses desde el congelamiento del GATE B

export function Laboratorio() {
  const { data, isLoading, error, refetch } = useApi<DatosHistorial>('/historial')

  if (isLoading)
    return (
      <div className="mx-auto grid max-w-6xl gap-4">
        <EsqueletoTiles />
        <EsqueletoCard alto="h-64" />
      </div>
    )
  if (error) return <ErrorCarga mensaje={String(error)} alReintentar={() => refetch()} />
  if (!data) return null
  const d = data.datos

  const nVerificadas = d.estados.find((e) => e.Estado === 'verificada')?.N ?? 0
  const regimenes = new Set(
    d.snapshots.map((s) => s['Régimen']).filter((r) => r != null && r !== ''),
  )
  const cambioRegimen = regimenes.size >= 2

  return (
    <div className="mx-auto grid max-w-6xl gap-4">
      {/* estado del experimento */}
      <Card className="capa-1">
        <div className="mb-3 flex items-baseline gap-3">
          <h2 className="font-display text-[15px] font-semibold text-text-1">
            El laboratorio — backtest walk-forward B0→B5
          </h2>
          <span className="rounded border border-border bg-bg-2 px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-2">
            en espera de madurez del track record
          </span>
        </div>
        <p className="mb-4 max-w-3xl text-xs leading-relaxed text-text-2">
          El motor está construido, probado (test de no-look-ahead del propio
          framework incluido) y validado: reproduce las predicciones selladas
          reales con diferencia media de 0.05 pp. Su ejecución con veredicto
          espera el gatillo congelado en el GATE B — y aun cumplido, disparar
          la corrida es una decisión humana. El diseño completo, con métricas
          y criterios pre-registrados, vive en{' '}
          <span className="num">backtest/DISEÑO.md</span>.
        </p>
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-3">
          <StatTile
            etiqueta="Verificaciones limpias"
            valor={`${nVerificadas}/${OBJETIVO_N}`}
            detalle="condición (a): N ≥ 150 en vivo…"
          />
          <StatTile
            etiqueta="Cambio de régimen"
            valor={cambioRegimen ? 'observado' : 'aún no'}
            detalle={`…Y al menos un cambio (regímenes sellados vistos: ${regimenes.size || '—'})`}
          />
          <StatTile
            etiqueta="O bien, operación continua"
            valor={FECHA_LIMITE}
            detalle="condición (b): 3 meses desde el 25-jul-2026 — lo que llegue primero"
          />
        </div>
      </Card>

      {/* el diseño del experimento */}
      <Card titulo="Seis baselines, seis preguntas" className="capa-2">
        <ul className="divide-y divide-border">
          {BASELINES.map((b) => (
            <li key={b.id} className="flex items-baseline gap-3 py-2 text-xs">
              <span className="num w-8 shrink-0 text-text-1">{b.id}</span>
              <span className="w-72 shrink-0 text-text-2">{b.nombre}</span>
              <span className="min-w-0 flex-1 text-text-3">{b.pregunta}</span>
            </li>
          ))}
        </ul>
        <p className="mt-2 border-t border-border pt-2 text-[11px] leading-relaxed text-text-3">
          Veredicto ESCALONADO: cada capa se compara contra la anterior (ΔIC
          con t de Newey-West &gt; 2) — el resultado es un mapa de qué capa
          aporta información y cuál es peso muerto, no un sí/no global.
        </p>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card titulo="Integridad del experimento" className="capa-3">
          <ul className="grid gap-2 text-xs leading-relaxed text-text-2">
            <li>
              · <span className="text-text-1">Gap vs capturable:</span> el gap
              (apertura vs cierre anterior) mide si la señal existe, pero es
              incomprable — la emisión ocurre cuando ese cierre ya pasó. La
              cartera simulada solo opera lo posible: apertura → cierre.
            </li>
            <li>
              · <span className="text-text-1">Point-in-time con grados:</span>{' '}
              todo resultado se etiqueta grado A (insumos verificables:
              precios recortados por la vía auditada del motor, sellos) o
              grado B (sentimiento pre-sello, sesgo de universo) — declarado,
              nunca escondido.
            </li>
            <li>
              · <span className="text-text-1">Costos:</span> 25 pb por lado
              (caso base), sensibilidad obligatoria 10/25/50. Una estrategia
              que solo vive con 10 pb no aprueba.
            </li>
            <li>
              · <span className="text-text-1">Benchmark obligatorio:</span>{' '}
              buy-and-hold de SMH en toda tabla y gráfico — "¿le gana a
              comprar SMH y no hacer nada?" siempre tiene respuesta explícita.
            </li>
            <li>
              · <span className="text-text-1">Sin p-hacking:</span> métricas,
              ventanas, costos y criterios de veredicto quedaron congelados en
              el diseño ANTES del primer resultado.
            </li>
          </ul>
        </Card>

        <Card titulo="Estado de la maquinaria" className="capa-3">
          <ul className="grid gap-2 text-xs leading-relaxed text-text-2">
            <li>
              · Suite propia en verde, incluido el test que INYECTA un dato
              futuro y verifica que el framework lo rechaza, y la prueba de
              que truncar el futuro no cambia ninguna predicción emitida.
            </li>
            <li>
              · Corrida de humo sobre datos legacy ejecutada y marcada{' '}
              <span className="text-warn">NO-CONCLUYENTE</span> en toda
              salida (backtest/resultados/).
            </li>
            <li>
              · Auditoría de reproducción: B2 (el modelo congelado) replica
              las predicciones selladas reales con diferencia media 0.05 pp y
              máxima 0.28 pp — la deriva de datos de la fuente, no un bug.
            </li>
            <li>
              · Solo lectura por construcción: las bases de producción se
              abren en modo ro; los resultados viven en su propia carpeta.
            </li>
          </ul>
          <p className="mt-3 border-t border-border pt-2 text-[11px] text-text-3">
            Herramienta de análisis — no constituye asesoría financiera. Hoy
            no opera dinero y no genera órdenes.
          </p>
        </Card>
      </div>
    </div>
  )
}
