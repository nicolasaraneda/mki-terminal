import { EmptyState } from '../componentes/EmptyState'

// Marcador de posición mientras las vistas se migran fase a fase (F3–F5).
// El dashboard Streamlit sigue disponible como respaldo en :8501.
export function EnConstruccion({ vista }: { vista: string }) {
  return (
    <EmptyState
      titulo={`${vista}: migración en curso`}
      detalle="Esta vista llega en una fase posterior de la Etapa 4.7. Mientras tanto, el dashboard Streamlit (puerto 8501) sigue operativo."
    />
  )
}
