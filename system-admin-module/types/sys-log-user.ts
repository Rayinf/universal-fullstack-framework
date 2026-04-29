/**
 * 用户日志相关类型定义
 */

// 基础API响应类型
export interface SysLogUserApiResponse<T = any> {
  code: number
  msg: string
  data?: T  // data字段可选，因为后端可能不返回data
}

// 用户日志记录
export interface SysLogUserRecord {
  id: number
  content: string
  type: number
  sysLogId: number
  creator: string
  createBy: number
  createTime: string
  realName: string
}

// 用户日志查询参数
export interface SysLogUserPageQuery {
  sortColumn?: string
  sortType?: string
  type?: number
  content?: string
  username?: string
  startTime?: string
  endTime?: string
  tenantCode?: string
}

// 分页请求
export interface SysLogUserPageRequest {
  records?: any[]
  total?: number
  size: number
  current: number
  optimizeJoinOfCountSql?: boolean
  pages?: number
}

// 分页响应
export interface SysLogUserIPage<T> {
  size: number
  total: number
  current: number
  records: T[]
  pages: number
}

// 日志导出参数
export interface SysLogUserExportQuery {
  sortColumn?: string
  sortType?: string
  type?: number
  content?: string
  username?: string
  startTime?: string
  endTime?: string
  tenantCode?: string
}

// 日志类型枚举
export const LogType = {
  USER: 0,         // 普通用户日志
  ADMIN: 1         // 管理员日志
} as const

// 清空类型枚举
export const ClearType = {
  WEEK: 1,         // 最近一周
  MONTH: 2,        // 最近一个月
  THREE_MONTHS: 3, // 最近3个月
  HALF_YEAR: 4,    // 最近半年
  YEAR: 5,         // 最近一年
  THREE_YEARS: 6,  // 最近三年
  ALL: 9           // 全部
} as const

// 排序类型枚举
export const SortType = {
  ASC: 'asc',      // 升序
  DESC: 'desc'     // 降序
} as const



