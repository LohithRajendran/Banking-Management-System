// vite.config.js — Build tool configuration
// Vite is a modern, super-fast build tool for React apps.
// This config:
//   1. Enables React (with JSX support)
//   2. Sets up a proxy so /api requests go to Django (no CORS issues in dev)

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,  // React runs on http://localhost:5173

    // PROXY: During development, when React calls /api/...,
    // Vite forwards the request to http://localhost:8000/api/...
    // This avoids CORS issues in development.
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
