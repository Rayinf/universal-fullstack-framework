// HMR 测试 - 修改时间: 2026-01-12 19:30
import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref, computed } from 'vue'
import { MOCK_ENABLED } from '../mock/mockConfig'
import { authService, userService } from '../mock/mockService'
import service from '../utils/request'
import { isSuccessCode } from '../utils/apiResponse'
import {
  clearAuthClientState,
  getStoredAuthTokens,
  getStoredUserRoleIds,
  migrateLegacyTokenStorage,
  persistSessionTokens,
  saveUserRoleIds,
} from '../utils/auth'
import { useMenuStore } from './menuStore'

// 角色ID到角色名称的映射
const roleIdToNameMapping: Record<string, string> = {
  '1': '系统管理员',
  '2': '任务录入员',
  '3': '计划员',
  '4': '工艺技术员',
  '5': '生产操作工',
  '6': '生产管理员',
  '7': '质量检验员',
  '8': '质量工程师',
  '9': '质量负责人',
  '10': '售后工程师',
  '11': '部门领导',
}

// 用户接口定义
interface User {
  id: string
  username: string
  name: string
  role: string
  region?: string
  phone?: string
  email?: string
  avatar?: string | null
  deptName?: string
  deptId?: string
}

// 销售人员列表接口
interface SalesUser {
  userId: string
  username: string
  realName?: string
}

// 用户信息更新接口
interface UserInfoUpdate {
  name?: string
  region?: string
  phone?: string
  email?: string
}

// 后端返回的登录响应结构
interface TokenResponse {
  token_type: string
  access_token: string
  refresh_token: string
}

// 用户信息API响应结构
interface UserInfoApiResponseData {
  sysUser: {
    userId: string
    username: string
    phone: string
    email: string | null
    avatar: string | null
    deptId: string
    realName: string
    tenantCode: string
    region?: string
  }
  deptName: string
  roles: string[]
  permissions: string[]
}

interface GetAllUserItem {
  userId: string | number
  username: string
  realName?: string
}

export const useUserStore = defineStore('user', () => {
  // 当前登录的用户信息
  const currentUser = ref<User | null>(null)

  // Token 信息
  const tokenType = ref<string | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  // 租户名称
  const tenantName = ref<string | null>(null)

  // 防止重复调用
  let isFetchingTenantName = false
  let isFetchingUserInfo = false

  // 用户列表
  const salesUsersList = ref<SalesUser[]>([])
  const isLoadingUsers = ref(false)

  // 应用初始化时从本地或会话存储恢复用户状态
  const initializeUserState = async () => {
    migrateLegacyTokenStorage()
    const storedTokens = getStoredAuthTokens()

    if (storedTokens) {
      accessToken.value = storedTokens.accessToken
      refreshToken.value = storedTokens.refreshToken
      tokenType.value = storedTokens.tokenType

      try {
        await fetchUserInfo()
      } catch (error) {
        console.error('恢复用户状态失败:', error)
        logout()
      }
    }
  }

  // 获取所有用户列表
  const fetchAllUsers = async () => {
    if (isLoadingUsers.value) return
    if (!accessToken.value) return

    isLoadingUsers.value = true
    try {
      if (MOCK_ENABLED) {
        const response = await userService.getAllUsers()
        if (isSuccessCode(response.code) && Array.isArray(response.data)) {
          salesUsersList.value = response.data.map((user) => ({
            userId: user.userId != null ? user.userId.toString() : '',
            username: user.username,
            realName: user.realName || user.username,
          }))
        }
      } else {
        const response = await service.get<GetAllUserItem[]>('/admin/user/getAllUser')
        if (isSuccessCode(response.code) && Array.isArray(response.data)) {
          salesUsersList.value = response.data.map((user) => ({
            userId: user.userId != null ? user.userId.toString() : '',
            username: user.username,
            realName: user.realName || user.username,
          }))
        }
      }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      salesUsersList.value = []
    } finally {
      isLoadingUsers.value = false
    }
  }

  // 根据userId查找用户名
  const getUserNameById = (userId: number | string | null | undefined): string => {
    if (userId === null || userId === undefined) return ''
    const user = salesUsersList.value.find((u) => u.userId === userId.toString())
    return user?.realName || user?.username || ''
  }

  // 根据用户名查找userId
  const getUserIdByName = (name: string): string => {
    const user = salesUsersList.value.find((u) => u.realName === name || u.username === name)
    return user?.userId || ''
  }

  // 获取用户角色数组
  const getUserRoles = (): string[] => {
    return getStoredUserRoleIds()
  }

  // 判断当前用户是否为超级管理员
  const isSuperAdmin = computed(() => {
    if (!currentUser.value) return false
    const roles = getUserRoles()
    return roles.includes('1') && currentUser.value.region === '0000'
  })

  // 判断当前用户是否为管理员
  const isAdmin = computed(() => {
    if (!currentUser.value) return false
    const roles = getUserRoles()
    return roles.includes('1')
  })

  // 判断当前用户是否可以查看参数管理
  const canViewParameterSettings = computed(() => {
    if (!currentUser.value) return false
    const roles = getUserRoles()
    return roles.includes('3') || roles.includes('4') || roles.includes('1')
  })

  // 判断当前用户是否可以查看人员管理
  const canViewUserManagement = computed(() => {
    if (!currentUser.value) return false
    const roles = getUserRoles()
    return roles.includes('1')
  })

  // 判断是否应该显示系统管理菜单
  const canViewSystemManagement = computed(() => {
    return canViewParameterSettings.value || canViewUserManagement.value
  })

  // 获取当前用户信息
  const getCurrentUser = () => {
    return currentUser.value
  }

  // 获取所有用户列表的getter
  const getAllSalesUsers = computed(() => {
    if (!Array.isArray(salesUsersList.value)) return []
    return salesUsersList.value.map((user) => ({
      id: user.userId,
      name: user.realName || user.username,
      username: user.username,
      userId: user.userId,
    }))
  })

  // 更新用户信息
  const updateUserInfo = (userInfo: UserInfoUpdate) => {
    if (currentUser.value) {
      currentUser.value = { ...currentUser.value, ...userInfo }
      return Promise.resolve(currentUser.value)
    }
    return Promise.reject('User not logged in')
  }

  // 获取租户名称
  const fetchTenantName = async () => {
    if (isFetchingTenantName) return null
    if (!accessToken.value) return null

    try {
      isFetchingTenantName = true

      if (MOCK_ENABLED) {
        const response = await authService.getTenantName()
        if (isSuccessCode(response.code)) {
          tenantName.value = response.data
        }
      } else {
        const response = await service.get<string>('/manage/api/tenant/getTenantName')
        if (isSuccessCode(response.code)) {
          tenantName.value = response.data
        }
      }
    } catch (error) {
      console.error('获取租户名称失败:', error)
      tenantName.value = null
    } finally {
      isFetchingTenantName = false
    }
  }

  // 获取并设置当前用户详细信息
  const fetchUserInfo = async () => {
    if (isFetchingUserInfo) return
    if (!accessToken.value) return

    isFetchingUserInfo = true
    try {
      if (MOCK_ENABLED) {
        const response = await authService.getUserInfo(accessToken.value)
        if (isSuccessCode(response.code) && response.data) {
          const userData = response.data
          const userRoleIds = userData.roles
          const roleName =
            userRoleIds.length > 0 ? roleIdToNameMapping[userRoleIds[0]] || '未知角色' : '未知角色'

          currentUser.value = {
            id: userData.sysUser.userId,
            username: userData.sysUser.username,
            name: userData.sysUser.realName,
            role: roleName,
            region: userData.sysUser.region || userData.sysUser.tenantCode,
            phone: userData.sysUser.phone,
            email: userData.sysUser.email || `${userData.sysUser.username}@mes.com`,
            avatar: userData.sysUser.avatar,
            deptName: userData.deptName,
            deptId: userData.sysUser.deptId,
          }

          saveUserRoleIds(userRoleIds)

          if (!tenantName.value && !isFetchingTenantName) {
            await fetchTenantName()
          }
        }
      } else {
        const response = await service.get<UserInfoApiResponseData>('/admin/user/info')
        if (isSuccessCode(response.code) && response.data) {
          const userData = response.data
          const userRoleIds = userData.roles
          const roleName =
            userRoleIds.length > 0 ? roleIdToNameMapping[userRoleIds[0]] || '未知角色' : '未知角色'

          currentUser.value = {
            id: userData.sysUser.userId,
            username: userData.sysUser.username,
            name: userData.sysUser.realName,
            role: roleName,
            region: userData.sysUser.region || userData.sysUser.tenantCode,
            phone: userData.sysUser.phone,
            email: userData.sysUser.email || `${userData.sysUser.username}@example.com`,
            avatar: userData.sysUser.avatar,
            deptName: userData.deptName,
            deptId: userData.sysUser.deptId,
          }

          saveUserRoleIds(userRoleIds)

          if (!tenantName.value && !isFetchingTenantName) {
            await fetchTenantName()
          }
        }
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    } finally {
      isFetchingUserInfo = false
    }
  }

  // 登录功能
  const login = async (loginData: TokenResponse, _rememberMe: boolean = true) => {
    tokenType.value = loginData.token_type
    accessToken.value = loginData.access_token
    refreshToken.value = loginData.refresh_token

    // Token 仅保存在会话存储，降低 XSS 风险窗口
    persistSessionTokens(loginData)

    // 登录成功后获取用户详细信息
    await fetchUserInfo()

    if (currentUser.value) {
      return Promise.resolve(currentUser.value)
    } else {
      tokenType.value = null
      accessToken.value = null
      refreshToken.value = null
      clearAuthClientState()
      return Promise.reject('获取用户信息失败')
    }
  }

  // 退出登录
  const logout = () => {
    const menuStore = useMenuStore()

    currentUser.value = null
    tokenType.value = null
    accessToken.value = null
    refreshToken.value = null
    tenantName.value = null
    salesUsersList.value = []

    clearAuthClientState()

    menuStore.reset()

    isFetchingUserInfo = false
    isFetchingTenantName = false

    return Promise.resolve()
  }

  return {
    currentUser,
    tokenType,
    accessToken,
    refreshToken,
    tenantName,
    isSuperAdmin,
    isAdmin,
    canViewParameterSettings,
    canViewUserManagement,
    canViewSystemManagement,
    getCurrentUser,
    updateUserInfo,
    login,
    logout,
    fetchTenantName,
    fetchUserInfo,
    getAllSalesUsers,
    initializeUserState,
    fetchAllUsers,
    getUserNameById,
    getUserIdByName,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUserStore, import.meta.hot))
}
