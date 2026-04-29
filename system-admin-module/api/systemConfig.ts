import request from '../utils/request'
import type { SystemConfigData, UpdateConfigRequest } from '../types/systemConfig'

// API响应结构
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

/**
 * 获取系统默认配置信息
 */
export const getSystemConfigApi = (): Promise<ApiResponse<SystemConfigData>> => {
  return request.get('/manage/api/systemConfig/getSystemDefaultData')
}

/**
 * 更新系统配置
 */
export const updateSystemConfigApi = (payload: UpdateConfigRequest): Promise<ApiResponse<any>> => {
  return request.put('/manage/api/systemConfig/update', payload)
}

/**
 * 批量更新系统配置
 */
export const updateAllConfigsApi = async (configs: SystemConfigData): Promise<boolean> => {
  const updates = [
    { code: 'companyName', value: configs.companyName },
    { code: 'systemName', value: configs.systemName },
    { code: 'version', value: configs.version },
  ]

  try {
    const results = await Promise.all(
      updates.map((update) =>
        updateSystemConfigApi({
          id: 0,
          code: update.code,
          value: update.value,
        })
      )
    )

    return results.every((res) => res.code === 200)
  } catch (error) {
    console.error('批量更新系统配置失败:', error)
    return false
  }
}
