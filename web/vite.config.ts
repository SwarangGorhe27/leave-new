/// <reference types="vite/client" />

import { defineConfig, loadEnv } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

function fromConfigRoot(relativePath: string) {
  const pathname = new URL(relativePath, import.meta.url).pathname
  const decoded = decodeURIComponent(pathname)
  return /^[A-Za-z]:/.test(decoded.slice(1)) ? decoded.slice(1) : decoded
}

function figmaAssetResolver() {
  return {
    name: 'figma-asset-resolver',
    resolveId(id: string) {
      if (id.startsWith('figma:asset/')) {
        const filename = id.replace('figma:asset/', '')
        return fromConfigRoot(`./src/assets/${filename}`)
      }
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_API_PROXY_TARGET || 'http://acme.localhost:8000'
  const defaultTenantHost = (() => {
    try {
      return new URL(backendTarget).host
    } catch {
      return 'acme.localhost:8000'
    }
  })()
  const tenantHost = env.VITE_TENANT_HOST || defaultTenantHost

  // File types to support raw imports. Never add .css, .tsx, or .ts files to this.
  
  return {
    plugins: [
      figmaAssetResolver(),
      react(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': fromConfigRoot('./src'),
        '@components': fromConfigRoot('./src/components'),
        '@pages': fromConfigRoot('./src/pages'),
        '@hooks': fromConfigRoot('./src/hooks'),
        '@store': fromConfigRoot('./src/store'),
        '@types': fromConfigRoot('./src/types'),
        '@api': fromConfigRoot('./src/api'),
        '@utils': fromConfigRoot('./src/lib'),
        '@assets': fromConfigRoot('./src/assets'),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
          configure: (proxy) => {
            proxy.on('proxyReq', (proxyReq) => {
              proxyReq.setHeader('Host', tenantHost)
            })
          },
        },
      },
    },
    assetsInclude: ['**/*.svg', '**/*.csv'],
  }
})
