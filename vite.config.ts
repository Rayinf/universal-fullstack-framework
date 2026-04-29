import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import type { Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// WebSocket 劫持脚本，用于修复 IP 访问时的 HMR 问题
const wsHijackScript = `
<script>
(function() {
  if (typeof window !== 'undefined') {
    var currentHost = window.location.hostname;
    var OriginalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {
      var fixedUrl = url;
      if (typeof url === 'string') {
        if (url.indexOf('localhost') !== -1 || url.indexOf('0.0.0.0') !== -1) {
          fixedUrl = url.replace(/localhost|0\\.0\\.0\\.0/g, currentHost);
          console.log('🔧 [HMR修复] WebSocket URL:', url, '->', fixedUrl);
        }
      }
      if (protocols !== undefined) {
        return new OriginalWebSocket(fixedUrl, protocols);
      }
      return new OriginalWebSocket(fixedUrl);
    };
    window.WebSocket.prototype = OriginalWebSocket.prototype;
    window.WebSocket.CONNECTING = OriginalWebSocket.CONNECTING;
    window.WebSocket.OPEN = OriginalWebSocket.OPEN;
    window.WebSocket.CLOSING = OriginalWebSocket.CLOSING;
    window.WebSocket.CLOSED = OriginalWebSocket.CLOSED;
    console.log('✅ [HMR修复] WebSocket劫持已安装，当前主机:', currentHost);
  }
})();
</script>`

// 自定义插件：在 HTML 的 <head> 最开始注入 WebSocket 劫持脚本
const hmrFixPlugin = (): Plugin => {
  return {
    name: 'hmr-fix-plugin',
    enforce: 'post', // 在所有其他插件之后执行
    transformIndexHtml: {
      order: 'post', // 在 HTML 转换的最后阶段执行
      handler(html) {
        // 在 <head> 标签后立即注入脚本
        return html.replace('<head>', `<head>${wsHijackScript}`)
      },
    },
  }
}

// 自定义插件来处理Excel文件的MIME类型
const excelMimeTypePlugin = (): Plugin => {
  return {
    name: 'excel-mime-type',
    configureServer(server) {
      server.middlewares.use((req: any, res: any, next: any) => {
        if (req.url && req.url.endsWith('.xlsx')) {
          res.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          )
        } else if (req.url && req.url.endsWith('.xls')) {
          res.setHeader('Content-Type', 'application/vnd.ms-excel')
        }
        next()
      })
    },
  }
}

const resolveManualChunk = (id: string): string | undefined => {
  if (!id.includes('node_modules')) return undefined

  if (
    id.includes('/node_modules/vue/') ||
    id.includes('/node_modules/vue-router/') ||
    id.includes('/node_modules/pinia/')
  ) {
    return 'framework-vendor'
  }

  if (id.includes('/node_modules/@element-plus/icons-vue/')) {
    return 'element-plus-icons'
  }

  if (id.includes('/node_modules/element-plus/')) {
    return 'element-plus-vendor'
  }

  if (
    id.includes('/node_modules/@floating-ui/') ||
    id.includes('/node_modules/async-validator/')
  ) {
    return 'element-plus-helpers'
  }

  if (id.includes('/node_modules/chart.js/') || id.includes('/node_modules/vue-chartjs/')) {
    return 'chartjs-vendor'
  }

  if (id.includes('/node_modules/zrender/')) {
    return 'zrender-vendor'
  }

  if (id.includes('/node_modules/echarts/')) {
    return 'echarts-vendor'
  }

  if (
    id.includes('/node_modules/xlsx/') ||
    id.includes('/node_modules/jszip/') ||
    id.includes('/node_modules/file-saver/')
  ) {
    return 'excel-vendor'
  }

  if (
    id.includes('/node_modules/starfish-editor/') ||
    id.includes('/node_modules/starfish-form/') ||
    id.includes('/node_modules/ace-builds/') ||
    id.includes('/node_modules/codemirror/') ||
    id.includes('/node_modules/@codemirror/') ||
    id.includes('/node_modules/@lezer/')
  ) {
    return 'editor-vendor'
  }

  if (
    id.includes('/node_modules/axios/') ||
    id.includes('/node_modules/dayjs/') ||
    id.includes('/node_modules/uuid/') ||
    id.includes('/node_modules/crypto-js/')
  ) {
    return 'utility-vendor'
  }

  return 'misc-vendor'
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isDev = mode !== 'production'
  const usePolling = process.env.VITE_USE_POLLING === '1'

  return {
    plugins: [
      ...(isDev ? [hmrFixPlugin()] : []),
      vue(),
      ...(isDev ? [vueDevTools()] : []),
      excelMimeTypePlugin(),
    ],
    server: {
      host: '0.0.0.0', // 监听所有地址
      port: 5173,
      strictPort: false,
      cors: true,
      hmr: {
        overlay: true,
      },
      watch: {
        usePolling,
        interval: 1000,
        binaryInterval: 1500,
        ignored: ['**/node_modules/**', '**/dist/**', '**/.git/**'],
      },
      proxy: {
        '/api': {
          target: env.VITE_DEV_SERVER_URL || 'http://127.0.0.1:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          secure: false,
        },
      },
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@sys': fileURLToPath(new URL('./system-admin-module', import.meta.url)),
      },
    },
    define: {
      __VUE_PROD_DEVTOOLS__: false,
      __VITE_API_BASE_URL__: JSON.stringify(
        mode === 'production' ? env.VITE_PROD_API_BASE_URL : env.VITE_API_BASE_URL,
      ),
      __VITE_DEV_LOGIN_API_URL__: JSON.stringify(env.VITE_DEV_LOGIN_API_URL),
      __VITE_PROD_LOGIN_API_URL__: JSON.stringify(env.VITE_PROD_LOGIN_API_URL),
    },
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia', 'element-plus'],
    },
    build: {
      sourcemap: isDev,
      rollupOptions: {
        output: {
          manualChunks: resolveManualChunk,
        },
      },
    },
  }
})
