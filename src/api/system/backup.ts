import request from '@/utils/request'
import type {
  BackupRecord,
  BackupQueryParams,
  BackupPageRequest,
  BackupStats,
  BackupPlan,
} from '@/types/system/backup'

// API响应结构
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

// 分页响应
interface PageResponse<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

/**
 * 分页查询备份记录
 */
export const pageBackupRecordsApi = (
  params: BackupQueryParams & BackupPageRequest,
): Promise<ApiResponse<PageResponse<BackupRecord>>> => {
  return request.get('/manage/api/sysBakInfo/page', params)
}

/**
 * 获取备份统计信息
 */
export const getBackupStatsApi = (): Promise<ApiResponse<BackupStats>> => {
  return request.get('/manage/api/sysBakInfo/page', { current: 1, size: 1 })
}

/**
 * 立即执行备份
 */
export const triggerBackupApi = (verificationCode?: string): Promise<ApiResponse<unknown>> => {
  return request.get('/manage/api/sysBakInfo/backup', { verificationCode })
}

/**
 * 删除备份记录
 */
export const deleteBackupRecordApi = (
  id: string,
  verificationCode?: string,
): Promise<ApiResponse<unknown>> => {
  return request.delete('/manage/api/sysBakInfo/del', { id, verificationCode })
}

/**
 * 下载备份文件
 */
export const downloadBackupApi = (id: string): Promise<Blob> => {
  return request.rawGet<Blob>(
    `/manage/api/sysBakInfo/download/${id}`,
    undefined,
    {
      responseType: 'blob',
      useQueue: false,
    },
  )
}

/**
 * 恢复备份
 */
export const restoreBackupApi = (id?: string): Promise<ApiResponse<unknown>> => {
  return request.get('/manage/api/sysBakInfo/recovery', id ? { id } : undefined)
}

/**
 * 获取备份计划配置
 */
export const getBackupPlansApi = (): Promise<ApiResponse<BackupPlan | BackupPlan[]>> => {
  return request.post('/manage/api/sysBakInfo/getSysBakConfigInfo')
}

/**
 * 创建/更新备份计划
 */
export const createBackupPlanApi = (plan: Partial<BackupPlan>): Promise<ApiResponse<unknown>> => {
  return request.post('/manage/api/sysBakInfo/saveScheduledTask', plan)
}

/**
 * 更新备份计划
 */
export const updateBackupPlanApi = (plan: BackupPlan): Promise<ApiResponse<unknown>> => {
  return request.post('/manage/api/sysBakInfo/saveScheduledTask', plan)
}

/**
 * 删除备份计划
 */
export const deleteBackupPlanApi = (id: string): Promise<ApiResponse<unknown>> => {
  return request.delete('/manage/api/sysBakInfo/del', { id })
}
