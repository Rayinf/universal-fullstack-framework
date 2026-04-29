// 系统日志相关类型定义

// 日志类型枚举
export enum LogType {
  NORMAL = 0, // 普通用户日志
  ADMIN = 1, // 管理员日志
}

// 清理类型枚举
export enum ClearType {
  WEEK = 1, // 最近一周
  MONTH = 2, // 最近一个月
  THREE_MONTHS = 3, // 最近3个月
  HALF_YEAR = 4, // 最近半年
  YEAR = 5, // 最近一年
  THREE_YEARS = 6, // 最近三年
  ALL = 9, // 全部
}

// 用户日志记录
export interface SysLogUserRecord {
  id: string | number
  type: LogType
  title?: string
  serviceId?: string
  createBy?: string | number
  createTime?: string
  updateTime?: string
  remoteAddr?: string
  userAgent?: string
  requestUri?: string
  method?: string
  params?: string
  time?: number
  delFlag?: string
  exception?: string
  tenantCode?: string
  username?: string
  // 扩展字段
  operator?: string
  content?: string
  module?: string
  action?: string
  request?: string
  response?: string
  sysLogId?: string | number
  creator?: string
  realName?: string
  ip?: string
}

// 用户日志VO
export interface SysLogUserVO extends SysLogUserRecord {
  userName?: string
}

// 用户日志分页查询参数
export interface SysLogUserPageQuery {
  sortColumn?: string
  sortType?: 'asc' | 'desc'
  type?: LogType // Deprecated? The API uses logType
  logType?: LogType // New field matching API
  username?: string
  content?: string
  operator?: string
  module?: string
  startTime?: string
  endTime?: string
  tenantCode?: string
  realName?: string
}

// 用户日志VO
export interface SysLogUserVO extends SysLogUserRecord {
  userName?: string
}

// 用户日志分页查询参数
export interface SysLogUserPageQuery {
  sortColumn?: string
  sortType?: 'asc' | 'desc'
  type?: LogType
  username?: string
  content?: string
  operator?: string
  module?: string
  startTime?: string
  endTime?: string
  tenantCode?: string
  realName?: string // Added
}

// 用户日志分页请求
export interface SysLogUserPageRequest {
  current: number
  size: number
  records?: any[]
  total?: number
  pages?: number
  optimizeJoinOfCountSql?: boolean // Added
}

// 清空日志请求
export interface ClearLogRequest {
  logType: LogType
  clearType: ClearType
}

// 操作日志类型（与SysLogUser相同）
export type OperationLogRecord = SysLogUserRecord
export type OperationLogPageQuery = SysLogUserPageQuery
export type SysLogUserQueryDto = SysLogUserPageQuery

// 日志详情
export interface LogDetail extends SysLogUserRecord {
  requestBody?: string
  responseBody?: string
}
