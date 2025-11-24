import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['.ngrok-free.app'],
    port: 3000,
    host: true
  },
  build: {
    target: 'esnext',
    outDir: 'dist'
  },
  define: {
    global: 'globalThis'
  }
})