// 备份管理相关类型定义

// 备份类型枚举
export enum BackupType {
  MANUAL = 1, // 手动备份
  AUTO = 2, // 自动备份
}

// 备份状态枚举
export enum BackupStatus {
  SUCCESS = 1, // 成功
  FAILED = 2, // 失败
  RUNNING = 3, // 进行中
}

// 备份记录
export interface BackupRecord {
  id: string
  name: string
  type: BackupType
  typeName?: string
  status: BackupStatus
  statusName?: string
  size?: number
  sizeStr?: string
  path?: string
  operator?: string
  operatorName?: string
  createdAt?: string
  createTime?: string
  remark?: string
  tenantCode?: string
}

// 备份查询参数
export interface BackupQueryParams {
  name?: string
  type?: BackupType
  status?: BackupStatus
  startTime?: string
  endTime?: string
  tenantCode?: string
}

// 备份分页请求
export interface BackupPageRequest {
  current: number
  size: number
}

// 备份统计
export interface BackupStats {
  total: number
  success: number
  failed: number
  totalSize?: number
  totalSizeStr?: string
}

// 备份计划
export interface BackupPlan {
  id?: string
  name: string
  enabled: boolean
  cronExpression: string // cron表达式
  retentionDays: number // 保留天数
  remark?: string
}
