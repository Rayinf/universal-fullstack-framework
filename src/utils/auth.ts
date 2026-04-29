export interface AuthTokenPayload {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface StoredAuthTokens {
  accessToken: string
  refreshToken: string
  tokenType: string
}

export const TOKEN_STORAGE_KEYS = {
  accessToken: 'access_token',
  refreshToken: 'refresh_token',
  tokenType: 'token_type',
} as const

export const USER_ROLE_STORAGE_KEY = 'user_roles'

const getStorage = (type: 'local' | 'session'): Storage | null => {
  if (typeof window === 'undefined') return null
  return type === 'local' ? window.localStorage : window.sessionStorage
}

const readTokensFromStorage = (storage: Storage | null): StoredAuthTokens | null => {
  if (!storage) return null

  const accessToken = storage.getItem(TOKEN_STORAGE_KEYS.accessToken)
  const refreshToken = storage.getItem(TOKEN_STORAGE_KEYS.refreshToken)
  const tokenType = storage.getItem(TOKEN_STORAGE_KEYS.tokenType)

  if (!accessToken || !refreshToken || !tokenType) {
    return null
  }

  return {
    accessToken,
    refreshToken,
    tokenType,
  }
}

export const clearTokenStorage = () => {
  const localStorageRef = getStorage('local')
  const sessionStorageRef = getStorage('session')

  localStorageRef?.removeItem(TOKEN_STORAGE_KEYS.accessToken)
  localStorageRef?.removeItem(TOKEN_STORAGE_KEYS.refreshToken)
  localStorageRef?.removeItem(TOKEN_STORAGE_KEYS.tokenType)
  sessionStorageRef?.removeItem(TOKEN_STORAGE_KEYS.accessToken)
  sessionStorageRef?.removeItem(TOKEN_STORAGE_KEYS.refreshToken)
  sessionStorageRef?.removeItem(TOKEN_STORAGE_KEYS.tokenType)
}

export const clearAuthClientState = () => {
  clearTokenStorage()
  getStorage('local')?.removeItem(USER_ROLE_STORAGE_KEY)
}

export const migrateLegacyTokenStorage = () => {
  const localStorageRef = getStorage('local')
  const sessionStorageRef = getStorage('session')

  if (!localStorageRef || !sessionStorageRef) return

  const legacyTokens = readTokensFromStorage(localStorageRef)
  if (!legacyTokens) return

  sessionStorageRef.setItem(TOKEN_STORAGE_KEYS.accessToken, legacyTokens.accessToken)
  sessionStorageRef.setItem(TOKEN_STORAGE_KEYS.refreshToken, legacyTokens.refreshToken)
  sessionStorageRef.setItem(TOKEN_STORAGE_KEYS.tokenType, legacyTokens.tokenType)

  localStorageRef.removeItem(TOKEN_STORAGE_KEYS.accessToken)
  localStorageRef.removeItem(TOKEN_STORAGE_KEYS.refreshToken)
  localStorageRef.removeItem(TOKEN_STORAGE_KEYS.tokenType)
}

export const persistSessionTokens = (loginData: AuthTokenPayload) => {
  const sessionStorageRef = getStorage('session')
  if (!sessionStorageRef) return

  clearTokenStorage()
  sessionStorageRef.setItem(TOKEN_STORAGE_KEYS.accessToken, loginData.access_token)
  sessionStorageRef.setItem(TOKEN_STORAGE_KEYS.refreshToken, loginData.refresh_token)
  sessionStorageRef.setItem(TOKEN_STORAGE_KEYS.tokenType, loginData.token_type)
}

export const getStoredAuthTokens = (): StoredAuthTokens | null => {
  return readTokensFromStorage(getStorage('session')) || readTokensFromStorage(getStorage('local'))
}

export const getStoredAccessToken = (): string | null => {
  return getStoredAuthTokens()?.accessToken || null
}

export const getStoredTokenType = (): string | null => {
  return getStoredAuthTokens()?.tokenType || null
}

export const hasStoredTokenTriplet = (): boolean => {
  return getStoredAuthTokens() !== null
}

export const saveUserRoleIds = (roleIds: string[]) => {
  getStorage('local')?.setItem(USER_ROLE_STORAGE_KEY, JSON.stringify(roleIds))
}

export const getStoredUserRoleIds = (): string[] => {
  const stored = getStorage('local')?.getItem(USER_ROLE_STORAGE_KEY)
  if (!stored) return []

  try {
    return JSON.parse(stored) as string[]
  } catch {
    return []
  }
}

export const getLoginApiPath = () => {
  if (
    typeof __VITE_DEV_LOGIN_API_URL__ !== 'undefined' &&
    typeof __VITE_PROD_LOGIN_API_URL__ !== 'undefined'
  ) {
    return import.meta.env.MODE === 'production'
      ? __VITE_PROD_LOGIN_API_URL__
      : __VITE_DEV_LOGIN_API_URL__
  }

  return import.meta.env.MODE === 'production'
    ? import.meta.env.VITE_PROD_LOGIN_API_URL || '/auth/oauth2/token'
    : import.meta.env.VITE_DEV_LOGIN_API_URL || '/api/auth/oauth2/token'
}
