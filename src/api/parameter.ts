import request from '@/utils/request'
import type {
  BasicInfoDto,
  BasicInfoPageQuery,
  BasicInfoRecord,
  BasicInfoIPage,
  BasicInfoPageRequest,
  ScanBindingProcessDto,
  ScanBindingProcessRecord,
} from '@/types/parameter'

interface ScanBindingProcessPageQuery {
  current?: number
  size?: number
  keyWord?: string
  sortColumn?: string
  sortType?: string
}

// 分页查询基础信息维护
export const pageBasicInfoApi = (params: BasicInfoPageQuery & BasicInfoPageRequest) =>
  request.get<BasicInfoIPage<BasicInfoRecord>>('/manage/api/basicInformation/page', params)

// 根据类型获取分类列表
export const listBasicInfoByTypeApi = (type: number) =>
  request.get<BasicInfoRecord[]>('/manage/api/basicInformation/list', { type })

// 新增分类
export const saveBasicInfoApi = (data: BasicInfoDto) => {
  const requestData: BasicInfoDto = {
    name: data.name,
    type: data.type,
  }

  // 如果有 parentId，则添加到请求数据中
  if (data.parentId !== undefined && data.parentId !== null) {
    requestData.parentId = data.parentId
  }

  return request.post<unknown>('/manage/api/basicInformation/save', requestData)
}

// 修改分类
export const updateBasicInfoApi = (data: BasicInfoDto) => {
  const requestData: BasicInfoDto = {
    id: data.id,
    name: data.name,
    type: data.type,
  }

  // 如果有 parentId，则添加到请求数据中
  if (data.parentId !== undefined && data.parentId !== null) {
    requestData.parentId = data.parentId
  }

  return request.post<unknown>('/manage/api/basicInformation/update', requestData)
}

// 根据id删除分类
export const deleteBasicInfoApi = (id: number) =>
  request.delete<unknown>(`/manage/api/basicInformation/${id}`)

// --- 扫码枪工序关联 API ---

// 分页查询扫码枪工序关联
export const pageScanBindingProcessApi = (params: ScanBindingProcessPageQuery) =>
  request.get<BasicInfoIPage<ScanBindingProcessRecord>>(
    '/manage/api/scanBindingProcess/page',
    {
      current: params.current || 1,
      size: params.size || 10,
      ...params,
    },
  )

// 新增扫码枪工序关联
export const saveScanBindingProcessApi = (data: ScanBindingProcessDto) =>
  request.post<unknown>('/manage/api/scanBindingProcess/save', data)

// 修改扫码枪工序关联
export const updateScanBindingProcessApi = (data: ScanBindingProcessDto) =>
  request.post<unknown>('/manage/api/scanBindingProcess/update', data)

// 删除扫码枪工序关联
export const deleteScanBindingProcessApi = (id: number) =>
  request.delete<unknown>(`/manage/api/scanBindingProcess/${id}`)
