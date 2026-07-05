import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// El frontend nunca habla con yfinance ni con las bases: todo pasa por la
// API de solo lectura (uvicorn en :8000). El proxy evita CORS en desarrollo.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
