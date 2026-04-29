/**
 * 用户日志API模块
 */
import { request } from '@/api/http'
import type {
  SysLogUserApiResponse,
  SysLogUserRecord,
  SysLogUserPageQuery,
  SysLogUserPageRequest,
  SysLogUserIPage,
  SysLogUserExportQuery
} from '@/types/sys-log-user'

// 分页查询所有日志
export const pageSysLogUserApi = (params: SysLogUserPageQuery & SysLogUserPageRequest) =>
  request<SysLogUserApiResponse<SysLogUserIPage<SysLogUserRecord>>>({
    url: '/admin/api/sysLogUser',
    method: 'get',
    params
  })

// 通过主键查询单条日志
export const getSysLogUserDetailApi = (id: number) =>
  request<SysLogUserApiResponse<SysLogUserRecord>>({
    url: `/admin/api/sysLogUser/${id}`,
    method: 'get'
  })

// 删除日志
export const deleteSysLogUserApi = (idList: number[]) =>
  request<SysLogUserApiResponse<unknown>>({
    url: '/admin/api/sysLogUser/deleteLog',
    method: 'get',
    params: { ids: idList.join(',') }
  })

// 清空用户日志
export const clearSysLogUserApi = (logType: number, clearType: number) =>
  request<SysLogUserApiResponse<unknown>>({
    url: '/admin/api/sysLogUser/clearLog',
    method: 'get',
    params: { logType, clearType }
  })

// 导出用户日志
export const exportSysLogUserApi = (data: SysLogUserExportQuery) => {
  return request<Blob>({
    url: '/admin/api/sysLogUser/exportLog',
    method: 'post',
    data,
    responseType: 'blob'
  })
}



