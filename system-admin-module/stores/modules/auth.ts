import { defineStore } from 'pinia'
import type { LoginPayload, MenuItem, UserInfo } from '@/types/auth'
import { storage } from '@/utils/storage'
import { request } from '@/utils/request'
import { useAuthMock } from '@/mocks/auth/auth.mock'
import { loginApi, logoutApi, menuApi } from '@/api/modules/auth'
// permissions.ts 不再用于菜单过滤，后端菜单树已按权限返回

interface AuthState {
  token: string | null
  tokenType: string | null
  refreshToken: string | null
  userInfo: UserInfo | null
  menus: MenuItem[]
}

// 用户信息API响应类型
interface UserInfoApiResponse {
  code: number
  msg: string | null
  data: {
    sysUser: {
      userId: string
      username: string
      name?: string
      realName?: string
      email?: string
      avatar?: string
      phone?: string
      tenantCode?: string
      deptId?: string
      lockFlag?: string
      delFlag?: string
      enabled?: number
      examineStatus?: number
    }
    deptName?: string
    // roles可能是字符串数组或对象数组
    roles: string[] | Array<{
      roleId: string
      roleName: string
    }>
    permissions: string[]
    spaceSize?: any
    spaceSizeStr?: string
    usedSize?: any
    usedSizeStr?: string
  }
}

// 登录响应类型
interface LoginResponse {
  access_token: string
  token_type: string
  refresh_token: string
  expires_in: number
  scope: string
}

const useMock = import.meta.env.VITE_USE_MOCK === 'true'
const mock = useAuthMock()

/**
 * 对菜单树按 sortOrder/order 排序
 */
const sortMenuTree = (menus: MenuItem[]): MenuItem[] =>
  [...menus]
    .map((item) => ({
      ...item,
      children: item.children ? sortMenuTree(item.children) : undefined,
    }))
    .sort((a, b) => {
      const orderA = a.meta?.order ?? 999
      const orderB = b.meta?.order ?? 999
      return orderA - orderB
    })

/**
 * 按允许的菜单 ID 集合过滤菜单树
 * 保留 ID 在集合中的节点，以及有可见子节点的父节点
 */
const filterMenuTreeByIds = (menus: MenuItem[], allowedIds: Set<string>): MenuItem[] => {
  const result: MenuItem[] = []
  for (const item of menus) {
    const itemId = String((item as any).id ?? '')
    const selfAllowed = itemId && allowedIds.has(itemId)
    const filteredChildren = item.children
      ? filterMenuTreeByIds(item.children, allowedIds)
      : undefined
    const hasVisibleChildren = filteredChildren && filteredChildren.length > 0
    if (selfAllowed || hasVisibleChildren) {
      result.push({
        ...item,
        children: hasVisibleChildren ? filteredChildren : undefined,
      })
    }
  }
  return result
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: storage.getToken(),
    tokenType: storage.getLocal<string>('tokenType'),
    refreshToken: storage.getLocal<string>('refreshToken'),
    userInfo: storage.getLocal<UserInfo>('userInfo'),
    menus: [],
  }),
  actions: {
    // 使用token登录（用于真实后端API）
    async loginWithToken(loginData: LoginResponse, rememberMe: boolean = false) {
      try {
        // 存储token信息
        const storageMethod = rememberMe ? localStorage : sessionStorage
        
        this.token = loginData.access_token
        this.tokenType = loginData.token_type
        this.refreshToken = loginData.refresh_token
        
        storageMethod.setItem('access_token', loginData.access_token)
        storageMethod.setItem('token_type', loginData.token_type)
        storageMethod.setItem('refresh_token', loginData.refresh_token)
        
        storage.setToken(loginData.access_token, rememberMe)
        storage.setLocal('tokenType', loginData.token_type)
        storage.setLocal('refreshToken', loginData.refresh_token)
        // 可能存在 user_info（从登录响应中带回），用于兜底
        if ((loginData as any).user_info) {
          storage.setLocal('loginUserInfoRaw', (loginData as any).user_info)
        }
        
        // 获取用户信息
        await this.fetchProfile()
        
        // 获取菜单
        await this.fetchMenus()
        
        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },
    
    // 模拟登录（保留原有功能）
    async login(payload: LoginPayload) {
      try {
        const response = await loginApi(payload)
        
        if (response.code === 200) {
          // 设置用户信息
          this.userInfo = response.data.user
          this.token = response.data.token
          
          // 存储token和用户信息
          storage.setToken(response.data.token, payload.remember || false)
          storage.setLocal('userInfo', response.data.user)
          
          return response.data.user
        } else {
          throw new Error(response.message || '登录失败')
        }
      } catch (error: any) {
        console.error('登录失败:', error)
        throw error
      }
    },
    setUserInfo(userInfo: UserInfo) {
      this.userInfo = userInfo
      this.token = 'mock-token'
      storage.setToken('mock-token', true)
      storage.setLocal('userInfo', userInfo)
    },
    async initializeMenus() {
      this.menus = sortMenuTree(await mock.fetchMenus())
    },
    async logoutRemote() {
      try {
        // 调用后端登出接口
        const response = await logoutApi()
        if (response.code !== 200) {
          console.warn('后端登出接口返回错误:', response.message)
        }
      } catch (e) {
        // 后端登出失败不影响前端清理，本地继续进行
        console.warn('后端登出接口调用失败，继续清理本地状态', e)
      }
      // 统一走本地清理
      this.logout()
    },

    logout() {
      // 清除所有认证相关数据
      this.token = null
      this.tokenType = null
      this.refreshToken = null
      this.userInfo = null
      this.menus = []
      
      // 清除存储
      storage.clearToken()
      storage.removeLocal('userInfo')
      storage.removeLocal('tokenType')
      storage.removeLocal('refreshToken')
      
      // 清除session和local storage
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('token_type')
      sessionStorage.removeItem('refresh_token')
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_type')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_roles')
    },
    
    async fetchProfile() {
      try {
        // 注释掉缓存逻辑，强制重新获取用户信息以确保数据最新
        // if (this.userInfo) {
        //   return this.userInfo
        // }
        
        // 如果是 mock token，使用mock数据
        if (useMock || (this.token && this.token.startsWith('mock-token'))) {
          this.userInfo = await mock.fetchProfile()
          storage.setLocal('userInfo', this.userInfo)
          return this.userInfo
        }
        
        // 调用真实API获取用户信息
        console.log('开始调用 /api/admin/user/info 获取用户信息')
        const raw = await request.get<any>('/admin/user/info')
        console.log('用户信息API返回数据:', raw)

        // 兼容两种返回：1) {code,msg,data} 包装；2) 直接返回 data
        const wrapped = (raw && typeof raw === 'object' && 'code' in raw && 'data' in raw) ? raw as UserInfoApiResponse : null
        const payload = wrapped ? wrapped.data : raw

        if (payload && (payload.sysUser || payload.username || payload.user || payload.id || payload.userId)) {
          // 统一提取用户与权限字段（兼容多种返回结构）
          const sysUser = (payload as any).sysUser || (payload as any).user || payload
          console.log('提取的sysUser数据:', sysUser)
          console.log('sysUser.email:', sysUser.email)
          console.log('sysUser.phone:', sysUser.phone)
          const rawRoles = (payload as any).roles || sysUser.roles || (payload as any).authorities || []
          const rawPermissions = (payload as any).permissions || (payload as any).authorities || []

          // 规范化角色ID列表（支持字符串数组或对象数组）
          let normalizedRoleIds: string[] = []
          if (Array.isArray(rawRoles)) {
            if (rawRoles.length && typeof rawRoles[0] === 'object' && rawRoles[0] && 'roleId' in rawRoles[0]) {
              normalizedRoleIds = (rawRoles as Array<{ roleId: string }>).map(r => String(r.roleId))
            } else {
              // 可能是 ["1"] 或 ["ROLE_1"]
              normalizedRoleIds = (rawRoles as Array<string>).map(r => {
                if (typeof r !== 'string') return ''
                return r.startsWith('ROLE_') ? r.replace('ROLE_', '') : r
              }).filter(Boolean)
            }
          }

          // 直接使用角色ID，不再需要映射为命名角色
          // 新的权限系统直接基于角色ID进行权限控制
          const mergedRoles = normalizedRoleIds

          // 转换为前端用户信息格式
          this.userInfo = {
            id: String(sysUser.userId ?? sysUser.id ?? ''),
            username: sysUser.username ?? sysUser.account ?? sysUser.loginName ?? '',
            name: sysUser.realName || sysUser.name || sysUser.username || '',
            avatar: sysUser.avatar || '',
            email: sysUser.email || '',
            phone: sysUser.phone || '',
            roles: mergedRoles,
            permissions: Array.isArray(rawPermissions)
              ? rawPermissions.map((p: any) => typeof p === 'string' ? p : (p?.authority ?? '')).filter((x: string) => x && !x.startsWith('ROLE_'))
              : []
          }
          
          console.log('转换后的用户信息:', this.userInfo)
          console.log('转换后的email:', this.userInfo.email)
          console.log('转换后的phone:', this.userInfo.phone)

          // 保存用户角色到localStorage
          localStorage.setItem('user_roles', JSON.stringify(this.userInfo.roles))

          storage.setLocal('userInfo', this.userInfo)
          return this.userInfo
        } else {
          const msg = wrapped?.msg || '获取用户信息失败'
          throw new Error(msg)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 兜底：如果登录响应中带有 user_info，则用它初始化
        const fallback = storage.getLocal<any>('loginUserInfoRaw')
        if (fallback) {
          try {
            const sysUser = fallback
            const rawAuthorities: any[] = Array.isArray((fallback as any).authorities) ? (fallback as any).authorities : []
            const roleIds = rawAuthorities
              .map((a) => (typeof a === 'string' ? a : a?.authority ?? ''))
              .filter(Boolean)
              .map((s: string) => (s.startsWith('ROLE_') ? s.replace('ROLE_', '') : s))
              .filter((s: string) => /^\d+$/.test(s))
            this.userInfo = {
              id: String(sysUser.id ?? sysUser.userId ?? ''),
              username: sysUser.username ?? sysUser.account ?? sysUser.loginName ?? '',
              name: sysUser.realName || sysUser.name || sysUser.username || '',
              avatar: sysUser.avatar || '',
              roles: roleIds.length ? roleIds : ['1'],
              permissions: rawAuthorities
                .map((a) => (typeof a === 'string' ? a : a?.authority ?? ''))
                .filter((x: string) => x && !x.startsWith('ROLE_')),
            }
            storage.setLocal('userInfo', this.userInfo)
            localStorage.setItem('user_roles', JSON.stringify(this.userInfo.roles))
            return this.userInfo
          } catch (e) {
            console.error('fallback 解析失败:', e)
          }
        }
        throw error
      }
    },
    
    async fetchMenus() {
      try {
        console.log('开始获取菜单，当前用户角色:', this.userInfo?.roles)
        
        if (this.menus.length > 0) {
          return this.menus
        }
        
        // 1. 获取完整菜单树
        const response = await menuApi()
        
        if (response.code !== 200 && response.code !== 0) {
          throw new Error(response.message || '获取菜单失败')
        }
        
        let menuData = response.data

        // 2. 按角色过滤：获取当前用户角色可访问的菜单 ID
        const roleIds: string[] = this.userInfo?.roles ?? []
        if (roleIds.length > 0) {
          const idResults = await Promise.all(
            roleIds.map((rid) =>
              request<any>({ url: `/admin/menu/tree/${rid}`, method: 'get' }).catch(() => null),
            ),
          )
          const allowedIds = new Set<string>()
          for (const res of idResults) {
            if (res && (res.code === 0 || res.code === 200) && Array.isArray(res.data)) {
              res.data.forEach((id: string) => allowedIds.add(String(id)))
            }
          }
          if (allowedIds.size > 0) {
            menuData = filterMenuTreeByIds(menuData, allowedIds)
          }
        }

        this.menus = sortMenuTree(menuData)
        console.log('菜单加载完成:', this.menus)
        
        return this.menus
      } catch (error) {
        console.error('获取菜单失败，使用mock兜底:', error)
        const mockMenus = await mock.fetchMenus()
        this.menus = sortMenuTree(mockMenus)
        return this.menus
      }
    },
    
    // 初始化用户状态（应用启动时调用）
    async initializeUserState() {
      try {
        // 检查是否有存储的token
        const hasLocalToken = localStorage.getItem('access_token')
        const hasSessionToken = sessionStorage.getItem('access_token')
        
        if (hasLocalToken || hasSessionToken) {
          const tokenType = localStorage.getItem('token_type') || sessionStorage.getItem('token_type')
          const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
          
          this.token = hasLocalToken || hasSessionToken
          this.tokenType = tokenType
          this.refreshToken = refreshToken
          
          // 获取用户信息
          await this.fetchProfile()
          
          // 获取菜单
          await this.fetchMenus()
          
          return true
        }
        
        return false
      } catch (error) {
        console.error('初始化用户状态失败:', error)
        // 如果初始化失败，清除所有数据
        this.logout()
        return false
      }
    },

    // 清除菜单缓存（用于调试）
    clearMenuCache() {
      this.menus = []
      console.log('菜单缓存已清除')
    },
  },
  persist: true,
})
