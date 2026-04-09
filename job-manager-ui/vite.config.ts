import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'motion': ['framer-motion'],
        },
      },
    },
    target: 'esnext',
  },
  server: {
    host: true,
    port: 5173,
  },
  // Suppress TypeScript warnings for faster builds
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  }
})
