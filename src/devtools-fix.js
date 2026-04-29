// 修复Vue Devtools的"在编辑器中打开"功能和IP访问支持
// 重要：WebSocket 劫持必须在文件顶层立即执行，不能等待 load 事件！

if (typeof window !== 'undefined') {
  // 获取当前主机信息
  const currentHost = window.location.hostname
  const currentPort = window.location.port || '5173'
  const currentProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  console.log(
    `🔧 DevTools/HMR修复启动 - 当前地址: ${currentHost}:${currentPort}, 协议: ${currentProtocol}`,
  )

  // ============================================================
  // 关键修复：立即劫持 WebSocket，必须在 @vite/client 加载之前！
  // ============================================================
  const OriginalWebSocket = window.WebSocket
  window.WebSocket = function (url, protocols) {
    let fixedUrl = url
    if (typeof url === 'string') {
      // 修复 HMR WebSocket 连接地址（将 localhost/0.0.0.0 替换为当前主机）
      if (url.includes('localhost') || url.includes('0.0.0.0')) {
        fixedUrl = url.replace(/localhost|0\.0\.0\.0/g, currentHost)
        console.log('🔧 修复WebSocket连接URL:', url, '->', fixedUrl)
      }
    }
    if (protocols !== undefined) {
      return new OriginalWebSocket(fixedUrl, protocols)
    }
    return new OriginalWebSocket(fixedUrl)
  }
  // 保留原型链
  window.WebSocket.prototype = OriginalWebSocket.prototype
  window.WebSocket.CONNECTING = OriginalWebSocket.CONNECTING
  window.WebSocket.OPEN = OriginalWebSocket.OPEN
  window.WebSocket.CLOSING = OriginalWebSocket.CLOSING
  window.WebSocket.CLOSED = OriginalWebSocket.CLOSED

  // ============================================================
  // 立即劫持 fetch，用于修复编辑器打开等请求
  // ============================================================
  const originalFetch = window.fetch
  window.fetch = function (url, options) {
    if (url && typeof url === 'string') {
      // 处理编辑器打开功能
      if (url.includes('/__open-in-editor')) {
        if (url.includes('0.0.0.0') || url.includes('localhost')) {
          url = url.replace(/0\.0\.0\.0|localhost/g, currentHost)
        }
        console.log('🔧 修复编辑器打开URL:', url)
      }

      // 处理DevTools相关的请求
      if (url.includes('/__devtools') || url.includes('/@vite/client')) {
        if (url.startsWith('/')) {
          url = `${window.location.protocol}//${currentHost}:${currentPort}${url}`
        }
      }

      // 处理HMR相关的fetch请求
      if (url.includes('hmr') || url.includes('websocket')) {
        if (url.includes('localhost') || url.includes('0.0.0.0')) {
          url = url.replace(/localhost|0\.0\.0\.0/g, currentHost)
        }
        console.log('🔧 修复HMR连接URL:', url)
      }
    }
    return originalFetch(url, options)
  }

  // ============================================================
  // 页面加载后的额外检查（非关键路径）
  // ============================================================
  window.addEventListener('load', () => {
    // 强制启用DevTools
    if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
      window.__VUE_DEVTOOLS_GLOBAL_HOOK__.enabled = true
    }

    // 延迟检查HMR和DevTools状态
    setTimeout(() => {
      // 检查HMR连接
      const hmrConnected =
        window.__vite_is_modern_browser || document.querySelector('script[src*="/@vite/client"]')
      if (hmrConnected) {
        console.log('✅ HMR 连接正常')
      } else {
        console.warn('⚠️ HMR 连接可能有问题')
      }

      // 检查DevTools
      const devtoolsScript = document.querySelector('script[src*="vue-devtools"]')
      const devtoolsOverlay = document.querySelector('script[src*="overlay.js"]')
      if (devtoolsScript || devtoolsOverlay) {
        console.log('✅ Vue DevTools 脚本已加载')
      }
    }, 1000)

    console.log(`✅ DevTools和HMR修复已应用 - 访问地址: ${window.location.host}`)
  })

  // ============================================================
  // 监听HMR更新事件（用于调试）
  // ============================================================
  if (import.meta.hot) {
    import.meta.hot.on('vite:beforeUpdate', () => {
      console.log('🔄 HMR 更新开始')
    })

    import.meta.hot.on('vite:afterUpdate', () => {
      console.log('✅ HMR 更新完成')
    })

    import.meta.hot.on('vite:error', (err) => {
      console.error('❌ HMR 更新错误:', err)
    })

    // 接受自身的热更新
    import.meta.hot.accept()
  }
}
