import './assets/main.css'
import '@/styles/common.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { installElementPlus } from './plugins/elementPlus'
import { useUserStore } from './stores/userStore'

// 开发环境下的 HMR 防护：清理 Service Worker
if (import.meta.env.DEV) {
  void import('./devtools-fix.js')

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      for (const registration of registrations) {
        registration.unregister()
        console.log('✅ HMR 安全防护: 已注销 Service Worker')
      }
    })
  }

  // 清理 CacheStorage 避免旧资源干扰
  if ('caches' in window) {
    caches.keys().then((names) => {
      for (const name of names) {
        caches.delete(name)
        console.log(`✅ HMR 安全防护: 已清理缓存库 ${name}`)
      }
    })
  }
}

const init = async () => {
  const app = createApp(App)

  // 1. 挂载 Pinia
  const pinia = createPinia()
  app.use(pinia)

  // 2. 挂载插件
  installElementPlus(app)
  app.use(router)

  // 3. 注册图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  // 4. 初始化用户状态 (在 Pinia 挂载后)
  const userStore = useUserStore()
  userStore.initializeUserState().catch((e) => {
    console.error('User initialization error:', e)
  })

  // 5. 最后挂载 DOM
  app.mount('#app')
}

init()
