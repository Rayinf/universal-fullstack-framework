import request from '@/utils/request'
import type {
  OutsourcedDocumentInfo,
  OutsourcedDocumentSaveDTO,
  OutsourcedDocumentQueryDTO,
  PageResult,
} from '@/types/technology'

// 分页查询
export const getOutsourcedDocumentPage = (params: OutsourcedDocumentQueryDTO) => {
  return request.get<PageResult<OutsourcedDocumentInfo>>('/manage/api/outsourced/page', params)
}

// 获取列表
export const getOutsourcedDocumentList = () => {
  return request.get<OutsourcedDocumentInfo[]>('/manage/api/outsourced/list')
}

// 新增
export const saveOutsourcedDocument = (data: FormData) => {
  return request.post('/manage/api/outsourced/save', data)
}

// 更新基础信息
export const updateOutsourcedDocumentInfo = (data: any) => {
  return request.post('/manage/api/outsourced/update', data)
}

// 编辑文件 (修订)
export const updateOutsourcedDocumentFile = (data: FormData) => {
  return request.post('/manage/api/outsourced/updateFile', data)
}

// 修改状态
export const changeOutsourcedDocumentStatus = (id: string, fileStatus: number) => {
  return request.post(`/manage/api/outsourced/statusChange`, { id, fileStatus })
}

// 获取历史版本
export const getOutsourcedDocumentVersions = (fileId: string) => {
  return request.get<OutsourcedDocumentInfo[]>('/manage/api/outsourced/fileVersionList', {
    fileId,
  })
}

// 获取关联的工序库及参数
export const getOutsourcedDocumentRelations = (fileId: string) => {
  return request.get('/manage/api/outsourced/fileRelationLibraryAndItemList', { fileId })
}

// 在线预览 URL
export const getOutsourcedDocumentOnlineUrl = (fileId: string) => {
  return request.get<string>('/manage/api/outsourced/onlineFile', { fileId })
}

// 历史版本在线预览 URL
export const getOutsourcedDocumentHistoryOnlineUrl = (fileId: string) => {
  return request.get<string>('/manage/api/outsourced/onlineHistoryFile', { fileId })
}

// 下载 URL
export const downloadOutsourcedDocument = (ids: string) => {
  return request.get('/manage/api/outsourced/downloadFile', { ids }, { responseType: 'blob' })
}

// 下载历史版本
export const downloadOutsourcedDocumentHistory = (ids: string) => {
  return request.get(
    '/manage/api/outsourced/downloadHistoryFile',
    { ids },
    { responseType: 'blob' },
  )
}
