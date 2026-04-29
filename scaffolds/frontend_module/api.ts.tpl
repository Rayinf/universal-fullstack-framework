import request from '@/utils/request'
import type {
  __MODULE_PASCAL__PageData,
  __MODULE_PASCAL__PageParams,
  __MODULE_PASCAL__SaveDto,
  __MODULE_PASCAL__Record,
} from '@/types/__TYPE_DIR__/__MODULE_CAMEL__'

export const page__MODULE_PASCAL__Api = (params: __MODULE_PASCAL__PageParams) =>
  request.get<__MODULE_PASCAL__PageData>('__API_BASE_PATH__/page', params)

export const create__MODULE_PASCAL__Api = (data: __MODULE_PASCAL__SaveDto) =>
  request.post<unknown>('__API_BASE_PATH__', data)

export const update__MODULE_PASCAL__Api = (id: string, data: __MODULE_PASCAL__SaveDto) =>
  request.put<unknown>(`__API_BASE_PATH__/${id}`, data)

export const delete__MODULE_PASCAL__Api = (id: string) =>
  request.delete<unknown>(`__API_BASE_PATH__/${id}`)

export type { __MODULE_PASCAL__Record, __MODULE_PASCAL__SaveDto }
