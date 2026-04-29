const TOKEN_KEY = 'smt_token'

const setToken = (token: string, remember?: boolean) => {
  const storage = remember ? window.localStorage : window.sessionStorage
  storage.setItem(TOKEN_KEY, token)
}

const getToken = () => window.localStorage.getItem(TOKEN_KEY) ?? window.sessionStorage.getItem(TOKEN_KEY)

const clearToken = () => {
  window.localStorage.removeItem(TOKEN_KEY)
  window.sessionStorage.removeItem(TOKEN_KEY)
}

const setLocal = <T>(key: string, value: T) => {
  window.localStorage.setItem(key, JSON.stringify(value))
}

const getLocal = <T>(key: string): T | null => {
  const value = window.localStorage.getItem(key)
  return value ? (JSON.parse(value) as T) : null
}

const removeLocal = (key: string) => {
  window.localStorage.removeItem(key)
}

export const storage = {
  setToken,
  getToken,
  clearToken,
  setLocal,
  getLocal,
  removeLocal,
}
