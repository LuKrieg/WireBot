import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  publicDir: 'client/public',
  plugins: [tailwindcss()],
})
