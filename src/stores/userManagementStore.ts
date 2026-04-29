import { defineStore, acceptHMRUpdate } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// 角色接口定义
interface SysRole {
  roleId: string
  roleName: string
  roleCode: string
  roleDesc?: string
}

// 用户组接口定义（保持兼容性）
interface UserGroup {
  id: string
  name: string
}

// 租户接口定义
interface Tenant {
  id: string
  tenantCode: string
  tenantName: string
}

// 用户接口定义 - 根据后端API结构
interface User {
  userId: number
  username: string
  password?: string
  salt?: string
  createTime?: string
  updateTime?: string
  delFlag?: string
  lockFlag?: string
  phone?: string
  avatar?: string
  deptId?: number
  deptName?: string
  examiner?: number
  examinerName?: string
  examineStatus?: number
  examineContent?: string
  examineTime?: string
  enabled: 0 | 1 // 0: 启用, 1: 禁用
  realName: string
  createBy?: number
  creator?: string
  roleList: SysRole[]
  isAdmin?: boolean
  roleId?: string
  tenantCode?: string
  tenantName?: string
  email?: string
  // 为了兼容现有组件，添加映射字段
  id: string // 映射自 userId
  userName: string // 映射自 username
  userGroups: UserGroup[] // 从 roleList 映射
}

// 分页查询参数
interface UserQueryParams {
  current: number
  size: number
  username?: string
  tenantCode?: string
  roleId?: string
  enabled?: 0 | 1 | null
}

// 分页响应结构
interface PageResponse<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

// API响应结构
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

// 用户表单模型
export interface UserFormModel {
  id: string | null
  userName: string
  realName: string
  phone: string
  email?: string
  enabled: 0 | 1
  selectedUserGroupId: string | null
  selectedTenantId: string | null
  tenantCode?: string
  roleId?: string
  region?: string
}

export const useUserManagementStore = defineStore('userManagement', {
  state: () => ({
    users: [] as User[],
    userGroups: [] as UserGroup[], // 角色列表，映射为用户组
    roles: [] as SysRole[], // 真实的角色列表
    tenants: [] as Tenant[], // 租户列表
    loading: false,
    total: 0,
    // 查询条件
    queryParams: {
      current: 1,
      size: 10,
      username: '',
      tenantCode: '',
      roleId: '',
      enabled: null as 0 | 1 | null,
    } as UserQueryParams,
  }),

  getters: {
    totalUsers(state): number {
      return state.total
    },
    // 保持兼容性，但现在直接返回当前页数据
    paginatedUsers(state) {
      return (currentPage: number, pageSize: number): User[] => {
        return state.users
      }
    },
  },

  actions: {
    // 获取用户列表（分页查询）
    async fetchUsers(params?: Partial<UserQueryParams>) {
      this.loading = true
      try {
        // 更新查询参数
        if (params) {
          Object.assign(this.queryParams, params)
        }

        const response = await request.get<PageResponse<any>>('/admin/user/page', this.queryParams)

        if (response.code === 0 && response.data) {
          // 转换后端数据格式为前端需要的格式
          const roleMap = new Map(this.roles.map((r) => [String(r.roleId), r.roleName]))
          this.users = response.data.records.map((user: any) => ({
            ...user,
            id: user.userId ? user.userId.toString() : '',
            userName: user.username || '',
            userGroups: user.roleId
              ? [
                  {
                    id: user.roleId.toString(),
                    name: roleMap.get(String(user.roleId)) || '未知角色',
                  },
                ]
              : [],
            enabled: user.enabled ?? 0,
          }))
          this.total = response.data.total || 0
        } else {
          ElMessage.error(response.msg || '获取用户列表失败')
          this.users = []
          this.total = 0
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error('获取用户列表时发生网络错误')
        this.users = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },

    // 获取角色列表
    async fetchUserGroups() {
      try {
        // 尝试从API获取角色列表
        const response = await request.get<SysRole[]>('/admin/role/list')

        if (response.code === 0 && response.data) {
          this.roles = response.data
          // 映射为用户组格式以保持兼容性
          this.userGroups = response.data
            .filter((role) => role && role.roleId !== undefined && role.roleId !== null) // 过滤无效数据
            .map((role) => ({
              id: role.roleId.toString(),
              name: role.roleName || '未知角色',
            }))
        } else {
          this.userGroups = []
        }
      } catch (error) {
        console.error('获取角色列表失败:', error)
        this.userGroups = []
      }
    },

    // 获取租户列表
    async fetchTenants() {
      try {
        const response = await request.get<Tenant[]>('manage/api/tenant/queryList')

        if (response.code === 0 && response.data) {
          this.tenants = response.data.map((tenant: any) => ({
            id: tenant.code || '', // 使用 code 作为 ID
            tenantCode: tenant.code || '', // code 字段作为租户代码
            tenantName: tenant.name || '', // name 字段作为租户名称
          }))
        } else {
          ElMessage.error(response.msg || '获取租户列表失败')
          this.tenants = []
        }
      } catch (error) {
        console.error('获取租户列表失败:', error)
        ElMessage.error('获取租户列表时发生网络错误')
        this.tenants = []
      }
    },

    // 添加用户
    async addUser(newUser: Omit<UserFormModel, 'id'>) {
      this.loading = true
      try {
        // 根据选择的租户ID获取租户代码
        const selectedTenant = this.tenants.find((t) => t.id === newUser.selectedTenantId)
        const tenantCode = selectedTenant ? selectedTenant.tenantCode : newUser.tenantCode || ''

        const userData = {
          username: newUser.userName,
          password: '123456', // 默认密码
          phone: newUser.phone || '',
          enabled: newUser.enabled,
          realName: newUser.realName,
          tenantCode: tenantCode,
          email: newUser.email || '',
          region: newUser.region || '',
          role: newUser.selectedUserGroupId ? [parseInt(newUser.selectedUserGroupId)] : [],
          // 其他可选字段设置默认值
          lockFlag: '0',
          delFlag: '0',
          deptId: 0,
          examiner: 0,
          examineStatus: 0,
          examineContent: '',
          spaceSize: 0,
          post: [],
          password1: '123456',
          newpassword1: '123456',
        }

        const response = await request.post('/admin/user', userData)

        if (response.code === 0) {
          ElMessage.success('用户添加成功')
          // 重新获取用户列表
          await this.fetchUsers()
        } else {
          ElMessage.error(response.msg || '用户添加失败')
        }
      } catch (error) {
        console.error('添加用户失败:', error)
        ElMessage.error('添加用户时发生网络错误')
      } finally {
        this.loading = false
      }
    },

    // 更新用户
    async updateUser(updatedUser: UserFormModel) {
      this.loading = true
      try {
        const userData = {
          userId: updatedUser.id,
          realName: updatedUser.realName,
          phone: updatedUser.phone,
          role: updatedUser.selectedUserGroupId ? [parseInt(updatedUser.selectedUserGroupId)] : [],
          email: updatedUser.email || '',
          region: updatedUser.region || '',
        }

        const response = await request.put('/admin/user', userData)

        if (response.code === 0) {
          ElMessage.success('用户信息更新成功')
          // 重新获取用户列表
          await this.fetchUsers()
        } else {
          ElMessage.error(response.msg || '用户信息更新失败')
        }
      } catch (error) {
        console.error('更新用户失败:', error)
        ElMessage.error('更新用户时发生网络错误')
      } finally {
        this.loading = false
      }
    },

    // 删除用户
    async deleteUser(userId: string) {
      this.loading = true
      try {
        const response = await request.delete(`/admin/user/${userId}`)

        if (response.code === 0) {
          ElMessage.success('用户删除成功')
          // 重新获取用户列表
          await this.fetchUsers()
        } else {
          ElMessage.error(response.msg || '用户删除失败')
        }
      } catch (error) {
        console.error('删除用户失败:', error)
        ElMessage.error('删除用户时发生网络错误')
      } finally {
        this.loading = false
      }
    },

    // 更新用户状态
    async updateUserStatus(userId: string, enabled: 0 | 1) {
      try {
        const response = await request.get(`/admin/user/enabled?id=${userId}&type=${enabled}`)

        if (response.code === 0) {
          ElMessage.success(`用户${enabled === 0 ? '启用' : '禁用'}成功`)
          // 更新本地状态
          const user = this.users.find((u) => u.id === userId)
          if (user) {
            user.enabled = enabled
          }
        } else {
          ElMessage.error(response.msg || '用户状态更新失败')
          // 恢复原状态
          const user = this.users.find((u) => u.id === userId)
          if (user) {
            user.enabled = enabled === 0 ? 1 : 0
          }
        }
      } catch (error) {
        console.error('更新用户状态失败:', error)
        ElMessage.error('更新用户状态时发生网络错误')
        // 恢复原状态
        const user = this.users.find((u) => u.id === userId)
        if (user) {
          user.enabled = enabled === 0 ? 1 : 0
        }
      }
    },

    // 重置用户密码
    async resetUserPassword(userId: string) {
      this.loading = true
      try {
        const response = await request.get(`/admin/user/resetPwd`, {
          id: userId,
        })

        if (response.code === 0) {
          ElMessage.success('密码重置成功，已重置为默认密码')
        } else {
          ElMessage.error(response.msg || '密码重置失败')
        }
      } catch (error) {
        console.error('重置密码失败:', error)
        ElMessage.error('重置密码时发生网络错误')
      } finally {
        this.loading = false
      }
    },

    // 设置查询条件
    setQueryParams(params: Partial<UserQueryParams>) {
      Object.assign(this.queryParams, params)
    },

    // 重置查询条件
    resetQueryParams() {
      this.queryParams = {
        current: 1,
        size: 10,
        username: '',
        tenantCode: '',
        roleId: '',
        enabled: null,
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUserManagementStore, import.meta.hot))
}
