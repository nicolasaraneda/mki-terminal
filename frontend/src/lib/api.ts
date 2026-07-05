import { useQuery } from '@tanstack/react-query'
import type { DatosAperturas, DatosHoy, DatosSalud, Sobre } from './tipos'

// Única puerta al backend: GET al proxy /api (uvicorn :8000). El frontend
// jamás computa una señal — solo presenta lo que la API sirve.
async function traer<T>(ruta: string): Promise<Sobre<T>> {
  const r = await fetch(`/api${ruta}`)
  if (!r.ok) {
    const cuerpo = await r.json().catch(() => null)
    throw new Error(cuerpo?.detail ?? `Error ${r.status} en ${ruta}`)
  }
  return r.json()
}

const CINCO_MIN = 5 * 60 * 1000

export function useApi<T>(ruta: string, opciones?: { refrescoMs?: number }) {
  return useQuery({
    queryKey: [ruta],
    queryFn: () => traer<T>(ruta),
    staleTime: opciones?.refrescoMs ?? CINCO_MIN,
    refetchInterval: opciones?.refrescoMs,
  })
}

export const useHoy = () => useApi<DatosHoy>('/hoy')
export const useAperturas = () => useApi<DatosAperturas>('/aperturas')
export const useSalud = () => useApi<DatosSalud>('/salud')
