import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { Agent } from 'node:http'
import process from 'node:process'

// Debe coincidir con docker-compose (5005 → contenedor 5000). Desarrollo sin Docker: npm run dev:local
const backendTarget = process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:5005'

export default defineConfig({
  publicDir: 'client/public',
  plugins: [tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        agent: new Agent({ keepAlive: false }),
        // Evita cierre prematuro mientras el backend arranca o responde lento
        timeout: 120_000,
        proxyTimeout: 120_000
      }
    }
  }
})
