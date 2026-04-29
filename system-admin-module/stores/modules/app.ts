import { defineStore } from 'pinia'

interface AppState {
  isCollapse: boolean
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    isCollapse: false,
  }),
  actions: {
    toggleCollapse() {
      this.isCollapse = !this.isCollapse
    },
    setCollapse(value: boolean) {
      this.isCollapse = value
    },
  },
  persist: true,
})
