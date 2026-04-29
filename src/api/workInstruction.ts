import axios from 'axios'
import request from '@/utils/request'
import type {
  WorkInstructionInfo,
  WorkInstructionSaveDTO,
  WorkInstructionUpdateDTO,
  WorkInstructionQueryDTO,
  PageResult,
} from '@/types/technology'

// 获取API基础路径
const getApiBaseUrl = () => {
  if (typeof __VITE_API_BASE_URL__ !== 'undefined') {
    return __VITE_API_BASE_URL__
  }
  return import.meta.env.MODE === 'production'
    ? import.meta.env.VITE_PROD_API_BASE_URL || ''
    : import.meta.env.VITE_API_BASE_URL || '/api'
}

// 获取认证信息
const getAuthHeader = () => {
  const tokenType = localStorage.getItem('tokenType') || 'Bearer'
  const accessToken = localStorage.getItem('accessToken') || ''
  if (tokenType && accessToken) {
    return `${tokenType} ${accessToken}`
  }
  return ''
}

// 分页查询
export const getWorkInstructionPage = (params: WorkInstructionQueryDTO) => {
  return request.get<PageResult<WorkInstructionInfo>>('/manage/api/workInstruction/page', params)
}

// 获取列表
export const getWorkInstructionList = () => {
  return request.get<WorkInstructionInfo[]>('/manage/api/workInstruction/list')
}

// 新增
export const saveWorkInstruction = (data: FormData) => {
  return request.post('/manage/api/workInstruction/save', data)
}

// 更新基础信息
export const updateWorkInstructionInfo = (data: any) => {
  return request.post('/manage/api/workInstruction/update', data)
}

// 编辑文件 (修订)
export const updateWorkInstructionFile = (data: FormData) => {
  return request.post('/manage/api/workInstruction/updateFile', data)
}

// 修改状态
export const changeWorkInstructionStatus = (id: string, fileStatus: number) => {
  return request.post(`/manage/api/workInstruction/statusChange`, { id, fileStatus })
}

// 获取历史版本
export const getWorkInstructionVersions = (fileId: string) => {
  return request.get<WorkInstructionInfo[]>('/manage/api/workInstruction/fileVersionList', {
    fileId,
  })
}

// 获取关联的工序库及参数
export const getWorkInstructionRelations = (fileId: string) => {
  return request.get('/manage/api/workInstruction/fileRelationLibraryAndItemList', { fileId })
}

// 在线预览 URL
export const getWorkInstructionOnlineUrl = (fileId: string) => {
  return request.get<string>('/manage/api/workInstruction/onlineFile', { fileId })
}

// 历史版本在线预览 URL
export const getWorkInstructionHistoryOnlineUrl = (fileId: string) => {
  return request.get<string>('/manage/api/workInstruction/onlineHistoryFile', { fileId })
}

// 下载 URL (通常直接用 window.open 或 a 标签，不需要 axios 请求返回二进制流，除非特殊处理)
// 这里封装一个获取下载链接的方法，或者直接返回 axios promise 如果需要处理 blob
export const downloadWorkInstruction = (ids: string) => {
  return request.get('/manage/api/workInstruction/downloadFile', { ids }, { responseType: 'blob' })
}
