import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import { Layout } from './Layout'
import { Sistema } from './vistas/Sistema'
import { Hoy } from './vistas/Hoy'
import { Aperturas } from './vistas/Aperturas'
import { Cadena } from './vistas/Cadena'
import { Mercados } from './vistas/Mercados'
import { Comparador } from './vistas/Comparador'
import { Analisis } from './vistas/Analisis'
import { Historial } from './vistas/Historial'
import { Salud } from './vistas/Salud'
import { Laboratorio } from './vistas/Laboratorio'
import { Detalle } from './vistas/Detalle'
import { Operable } from './vistas/Operable'
import { RielDinero } from './vistas/RielDinero'
import { Rieles } from './vistas/Rieles'
import { SellosDinero } from './vistas/SellosDinero'

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
      { path: '/analisis', element: <Analisis /> },
      { path: '/historial', element: <Historial /> },
      { path: '/salud', element: <Salud /> },
      { path: '/laboratorio', element: <Laboratorio /> },
      // Riel de dinero (Etapa 7.0.0) — todo SIMULADO, ver VISION.md
      { path: '/rieles', element: <Rieles /> },
      { path: '/operable', element: <Operable /> },
      { path: '/dinero', element: <RielDinero /> },
      { path: '/sellos', element: <SellosDinero /> },
      { path: '/detalle/:ticker', element: <Detalle /> },
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
