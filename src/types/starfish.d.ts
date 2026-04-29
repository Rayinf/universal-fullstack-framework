declare module 'starfish-editor' {
  import { App } from 'vue'
  const StarfishEditor: {
    install: (app: App) => void
  }
  export default StarfishEditor
}

declare module 'starfish-form' {
  import { Component } from 'vue'
  export const Dynamicform: Component
}
