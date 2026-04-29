import request from '@/utils/request'
import type {
  WorkstationRecord,
  WorkstationQuery,
  WorkstationDTO,
  WorkstationIPage,
  WorkstationApiResponse,
} from '@/types/system/workstation'

// 分页查询工位
export const pageWorkstationsApi = (params: WorkstationQuery) =>
  request.get<WorkstationIPage>('/manage/api/workstation/page', params)

// 通过ID查询工位详情
export const getWorkstationDetailApi = (id: string) =>
  request.get<WorkstationRecord>(`/manage/api/workstation/${id}`)

// 添加工位
export const createWorkstationApi = (data: WorkstationDTO) =>
  request.post<WorkstationApiResponse<unknown>>('/manage/api/workstation/save', data)

// 更新工位信息
export const updateWorkstationApi = (data: WorkstationDTO) =>
  request.post<WorkstationApiResponse<unknown>>('/manage/api/workstation/update', data)

// 删除工位
export const deleteWorkstationApi = (id: string) =>
  request.delete<WorkstationApiResponse<unknown>>(`/manage/api/workstation/${id}`)

// 启用/禁用工位
export const toggleWorkstationStatusApi = (id: string, status: number) =>
  request.get<WorkstationApiResponse<unknown>>(`/manage/api/workstation/status/${id}`, { status })

// 获取所有工位信息
export const getAllWorkstationsApi = () =>
  request.get<WorkstationApiResponse<WorkstationRecord[]>>('/manage/api/workstation/list')
