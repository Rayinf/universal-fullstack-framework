import request from '@/utils/request'
import type {
  BasicCrudPageData,
  BasicCrudPageParams,
  BasicCrudSaveDto,
  BasicCrudRecord,
} from '@/types/system/basicCrud'

export const pageBasicCrudApi = (params: BasicCrudPageParams) =>
  request.get<BasicCrudPageData>('/local/crud/page', params)

export const createBasicCrudApi = (data: BasicCrudSaveDto) =>
  request.post<unknown>('/local/crud', data)

export const updateBasicCrudApi = (id: string, data: BasicCrudSaveDto) =>
  request.put<unknown>(`/local/crud/${id}`, data)

export const deleteBasicCrudApi = (id: string) =>
  request.delete<unknown>(`/local/crud/${id}`)

export type { BasicCrudRecord, BasicCrudSaveDto }
