/// <reference types="vite/client" />

// Vue 模块声明
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Vite define 变量声明
declare const __VITE_API_BASE_URL__: string
declare const __VITE_DEV_LOGIN_API_URL__: string
declare const __VITE_PROD_LOGIN_API_URL__: string

interface ImportMetaEnv {
  readonly VITE_LOGIN_BASIC_AUTH?: string
}

declare module '*.js'
