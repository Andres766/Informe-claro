import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// En desarrollo, /api se redirige al backend FastAPI (evita problemas de CORS).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
  },
})
