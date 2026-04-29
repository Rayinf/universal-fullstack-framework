// 系统配置数据接口
export interface SystemConfigData {
  companyName: string
  systemName: string
  version: string
}

// 更新配置的请求接口
export interface UpdateConfigRequest {
  id: number
  code: string
  value: string
}

// 配置项的代码常量
export const CONFIG_CODES = {
  COMPANY_NAME: 'companyName',
  SYSTEM_NAME: 'systemName',
  VERSION: 'version',
} as const

// 配置项代码类型
export type ConfigCode = typeof CONFIG_CODES[keyof typeof CONFIG_CODES]
