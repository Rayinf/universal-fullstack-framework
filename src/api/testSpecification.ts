import request from '@/utils/request'
import type {
  TestSpecificationInfo,
  TestSpecificationQueryDTO,
  PageResult,
} from '@/types/technology'

// 分页查询
export const getTestSpecificationPage = (params: TestSpecificationQueryDTO) => {
  return request.get<PageResult<TestSpecificationInfo>>(
    '/manage/api/testSpecification/page',
    params,
  )
}

// 获取列表
export const getTestSpecificationList = () => {
  return request.get<TestSpecificationInfo[]>('/manage/api/testSpecification/list')
}

// 新增
export const saveTestSpecification = (data: FormData) => {
  return request.post('/manage/api/testSpecification/save', data)
}

// 更新基础信息
export const updateTestSpecificationInfo = (data: any) => {
  return request.post('/manage/api/testSpecification/update', data)
}

// 编辑文件 (修订)
export const updateTestSpecificationFile = (data: FormData) => {
  return request.post('/manage/api/testSpecification/updateFile', data)
}

// 修改状态
export const changeTestSpecificationStatus = (id: string, fileStatus: number) => {
  return request.post(`/manage/api/testSpecification/statusChange`, { id, fileStatus })
}

// 获取历史版本
export const getTestSpecificationVersions = (fileId: string) => {
  return request.get<TestSpecificationInfo[]>('/manage/api/testSpecification/fileVersionList', {
    fileId,
  })
}

// 获取关联的工序库及参数
export const getTestSpecificationRelations = (fileId: string) => {
  return request.get('/manage/api/testSpecification/fileRelationLibraryAndItemList', { fileId })
}

// 在线预览 URL
export const getTestSpecificationOnlineUrl = (fileId: string) => {
  return request.get<string>('/manage/api/testSpecification/onlineFile', { fileId })
}

// 历史版本在线预览 URL
export const getTestSpecificationHistoryOnlineUrl = (fileId: string) => {
  return request.get<string>('/manage/api/testSpecification/onlineHistoryFile', { fileId })
}

// 下载 URL
export const downloadTestSpecification = (ids: string) => {
  return request.get(
    '/manage/api/testSpecification/downloadFile',
    { ids },
    { responseType: 'blob' },
  )
}

// 下载历史版本
export const downloadTestSpecificationHistory = (ids: string) => {
  return request.get(
    '/manage/api/testSpecification/downloadHistoryFile',
    { ids },
    { responseType: 'blob' },
  )
}
