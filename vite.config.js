import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { Agent } from 'node:http'

export default defineConfig({
  publicDir: 'client/public',
  plugins: [tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://[::1]:5005',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        agent: new Agent({ keepAlive: false })
      }
    }
  }
})
