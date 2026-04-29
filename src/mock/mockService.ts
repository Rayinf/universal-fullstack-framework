/**
 * Mock服务层
 * 提供模拟API接口 - 已对齐 orderInfo 后端结构
 */

import { MOCK_ENABLED, mockDelay, generateId } from './mockConfig'
import {
  mockCredentials,
  mockUsers,
  mockRoles,
  mockDepartments,
  mockTasks,
  mockSchedules,
  mockProducts,
  mockWorkOrders,
  mockInspections,
  mockNonconformities,
  mockEquipments,
  mockWorkstations,
  mockDashboardStats,
  mockProductionTrend,
  mockCapacityUtilization,
  mockQualityTrend,
} from './mockData'

// 标准API响应格式
interface ApiResponse<T = any> {
  code: number
  msg: string | null
  data: T
}

// 分页响应格式
interface PageResponse<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

// 创建成功响应
const success = <T>(data: T, msg: string | null = null): ApiResponse<T> => ({
  code: 0, // 已改为 0
  msg,
  data,
})

// 创建错误响应
const error = (msg: string, code: number = -1): ApiResponse<null> => ({
  code,
  msg,
  data: null,
})

// 创建分页响应
const paginate = <T>(list: T[], current: number = 1, size: number = 10): PageResponse<T> => {
  const total = list.length
  const pages = Math.ceil(total / size)
  const start = (current - 1) * size
  const records = list.slice(start, start + size)
  return { records, total, size, current, pages }
}

// ===================== 认证服务 =====================

export const authService = {
  async login(username: string, password: string): Promise<ApiResponse> {
    await mockDelay()
    if (mockCredentials[username] && mockCredentials[username] === password) {
      const user = mockUsers.find((u) => u.username === username)
      if (user) {
        return success({
          access_token: `mock_access_token_${user.userId}_${Date.now()}`,
          refresh_token: `mock_refresh_token_${user.userId}_${Date.now()}`,
          token_type: 'Bearer',
          expires_in: 43200,
        })
      }
    }
    return error('用户名或密码错误', 401)
  },

  async getUserInfo(token: string): Promise<ApiResponse> {
    await mockDelay()
    const match = token.match(/mock_access_token_(\d+)_/)
    const userId = match ? match[1] : '1'
    const user = mockUsers.find((u) => u.userId === userId) || mockUsers[0]
    return success({
      sysUser: {
        userId: user.userId,
        username: user.username,
        realName: user.realName,
        phone: user.phone,
        email: user.email,
        avatar: user.avatar,
        deptId: user.deptId,
        tenantCode: 'MES001',
      },
      deptName: user.deptName,
      roles: user.roles,
      permissions: ['*'],
    })
  },

  async getTenantName(): Promise<ApiResponse<string>> {
    await mockDelay()
    return success('MES演示企业')
  },
}

// ===================== 用户管理服务 =====================

export const userService = {
  async getAllUsers(): Promise<ApiResponse> {
    await mockDelay()
    return success(
      mockUsers.map((u) => ({
        userId: parseInt(u.userId),
        username: u.username,
        realName: u.realName,
      })),
    )
  },
}

// ===================== 任务管理服务 =====================

export const taskService = {
  async getTaskPage(params: any): Promise<ApiResponse> {
    await mockDelay()
    let list = [...mockTasks]

    if (params.progressStatus) {
      list = list.filter((t) => t.progressStatus === Number(params.progressStatus))
    }

    if (params.priority) {
      list = list.filter((t) => t.priority === Number(params.priority))
    }

    if (params.keyword) {
      const k = params.keyword.toLowerCase()
      list = list.filter(
        (t) =>
          t.orderNo.toLowerCase().includes(k) ||
          t.orderName.toLowerCase().includes(k) ||
          t.contractNo.toLowerCase().includes(k) ||
          t.customerName?.toLowerCase().includes(k) ||
          t.orderModel.toLowerCase().includes(k),
      )
    }

    return success(paginate(list, params.current || 1, params.size || 10))
  },

  async getTaskById(id: string): Promise<ApiResponse> {
    await mockDelay()
    const task = mockTasks.find((t) => String(t.id) === id)
    return task ? success(task) : error('任务不存在')
  },

  async createTask(data: any): Promise<ApiResponse> {
    await mockDelay()
    const now = new Date().toISOString().replace('T', ' ').slice(0, 19)
    const newTask = {
      id: 1000 + mockTasks.length,
      ...data,
      progressStatus: 1,
      createTime: now,
      creator: '管理员',
    }
    mockTasks.unshift(newTask as any)
    return success(newTask, '创建成功')
  },

  async updateTask(data: any): Promise<ApiResponse> {
    await mockDelay()
    const index = mockTasks.findIndex((t) => t.id === Number(data.id))
    if (index > -1) {
      mockTasks[index] = { ...mockTasks[index], ...data }
      return success(mockTasks[index], '更新成功')
    }
    return error('任务不存在')
  },

  async reviewTask(id: string): Promise<ApiResponse> {
    await mockDelay()
    const index = mockTasks.findIndex((t) => String(t.id) === id)
    if (index > -1) {
      mockTasks[index].progressStatus = 2
      mockTasks[index].verifier = '管理员'
      mockTasks[index].verificationTime = new Date().toISOString().replace('T', ' ').slice(0, 19)
      return success(null, '核查成功')
    }
    return error('任务不存在')
  },

  async submitTask(id: string): Promise<ApiResponse> {
    await mockDelay()
    const index = mockTasks.findIndex((t) => String(t.id) === id)
    if (index > -1) {
      mockTasks[index].progressStatus = 3
      mockTasks[index].submitter = '管理员'
      mockTasks[index].submissionTime = new Date().toISOString().replace('T', ' ').slice(0, 19)
      return success(null, '提交成功')
    }
    return error('任务不存在')
  },
}

// ===================== 计划排程服务 =====================

export const planningService = {
  async getSchedulePage(params: any): Promise<ApiResponse> {
    await mockDelay()
    const list = [...mockSchedules]
    return success(paginate(list, params.current || 1, params.size || 10))
  },

  async getScheduleById(id: string): Promise<ApiResponse> {
    await mockDelay()
    const schedule = mockSchedules.find((s) => s.id === id)
    return schedule ? success(schedule) : error('排程不存在')
  },

  async createSchedule(data: any): Promise<ApiResponse> {
    await mockDelay()
    const newSchedule = {
      id: generateId(),
      ...data,
      createdAt: new Date().toISOString(),
    }
    mockSchedules.push(newSchedule)
    return success(newSchedule)
  },

  async updateSchedule(id: string, data: any): Promise<ApiResponse> {
    await mockDelay()
    const index = mockSchedules.findIndex((s) => s.id === id)
    if (index === -1) return error('排程不存在')
    mockSchedules[index] = { ...mockSchedules[index], ...data }
    return success(mockSchedules[index])
  },

  async submitForApproval(scheduleIds: string[], approvers: string[]): Promise<ApiResponse> {
    await mockDelay()
    return success({ count: scheduleIds.length })
  },

  async approveSchedule(
    scheduleId: string,
    conclusion: string,
    opinion: string,
    nextApprovers?: string[],
  ): Promise<ApiResponse> {
    await mockDelay()
    return success(null)
  },

  async distributeSchedule(
    scheduleIds: string[],
    recipients: string[],
    note?: string,
  ): Promise<ApiResponse> {
    await mockDelay()
    return success({ count: scheduleIds.length })
  },
}

// ===================== 生产执行服务 =====================

export const productionService = {
  async getWorkOrderPage(params: any): Promise<ApiResponse> {
    await mockDelay()
    const list = [...mockWorkOrders]
    return success(paginate(list, params.current || 1, params.size || 10))
  },
}

// ===================== 质量监督服务 =====================

export const qualityService = {
  async getInspectionPage(params: any): Promise<ApiResponse> {
    await mockDelay()
    const list = [...mockInspections]
    return success(paginate(list, params.current || 1, params.size || 10))
  },
}

// ===================== 看板数据服务 =====================

export const dashboardService = {
  async getStats(): Promise<ApiResponse> {
    await mockDelay()
    return success(mockDashboardStats)
  },
}

// 导出统一的Mock服务
export const mockService = {
  auth: authService,
  user: userService,
  task: taskService,
  planning: planningService,
  production: productionService,
  quality: qualityService,
  dashboard: dashboardService,
  isMockEnabled: () => MOCK_ENABLED,
}

export default mockService
