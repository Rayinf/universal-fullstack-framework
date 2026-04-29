import request from '@/utils/request'
import type {
  SysLogUserRecord,
  SysLogUserPageQuery,
  SysLogUserPageRequest,
  ClearLogRequest,
  LogDetail,
} from '@/types/system/log'

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
 * 分页查询操作日志
 */
export const pageOperationLogApi = (
  params: SysLogUserPageQuery & SysLogUserPageRequest,
): Promise<ApiResponse<PageResponse<SysLogUserRecord>>> => {
  return request.get('/admin/api/sysLogUser', params)
}

/**
 * 获取操作日志详情
 */
export const getOperationLogDetailApi = (id: string | number): Promise<ApiResponse<LogDetail>> => {
  return request.get(`/admin/api/sysLogUser/${id}`)
}

/**
 * 删除操作日志 (单条)
 */
export const deleteSysLogUserApi = (id: string | number): Promise<ApiResponse<any>> => {
  return request.delete(
    '/admin/api/sysLogUser',
    { idList: [id] },
    {
      paramsSerializer: (params: any) => {
        const searchParams = new URLSearchParams()
        if (params.idList) {
          params.idList.forEach((id: any) => searchParams.append('idList', id))
        }
        return searchParams.toString()
      },
    },
  )
}

/**
 * 批量删除操作日志
 */
export const batchDeleteSysLogUserApi = (ids: (string | number)[]): Promise<ApiResponse<any>> => {
  return request.delete(
    '/admin/api/sysLogUser',
    { idList: ids },
    {
      paramsSerializer: (params: any) => {
        const searchParams = new URLSearchParams()
        if (params.idList) {
          params.idList.forEach((id: any) => searchParams.append('idList', id))
        }
        return searchParams.toString()
      },
    },
  )
}

/**
 * 清空操作日志
 */
export const clearSysLogUserApi = (params: ClearLogRequest): Promise<ApiResponse<any>> => {
  return request.get('/admin/api/sysLogUser/clearLog', params)
}

/**
 * 导出操作日志
 */
export const exportSysLogUserApi = (params: SysLogUserPageQuery): Promise<Blob> => {
  return request.post('/admin/api/sysLogUser/exportLog', params, {
    responseType: 'blob',
  }) as any
}
