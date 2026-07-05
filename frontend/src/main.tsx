import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import { Layout } from './Layout'
import { EnConstruccion } from './vistas/EnConstruccion'
import { Sistema } from './vistas/Sistema'
import { Hoy } from './vistas/Hoy'
import { Aperturas } from './vistas/Aperturas'
import { Cadena } from './vistas/Cadena'
import { Mercados } from './vistas/Mercados'
import { Comparador } from './vistas/Comparador'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
})

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Navigate to="/hoy" replace /> },
      { path: '/hoy', element: <Hoy /> },
      { path: '/aperturas', element: <Aperturas /> },
      { path: '/cadena', element: <Cadena /> },
      { path: '/mercados', element: <Mercados /> },
      { path: '/comparador', element: <Comparador /> },
      { path: '/analisis', element: <EnConstruccion vista="Análisis IA" /> },
      { path: '/historial', element: <EnConstruccion vista="Historial" /> },
      { path: '/detalle/:ticker', element: <EnConstruccion vista="Detalle" /> },
      // catálogo del sistema de diseño — oculto, sin enlace en la navegación
      { path: '/sistema', element: <Sistema /> },
    ],
  },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
