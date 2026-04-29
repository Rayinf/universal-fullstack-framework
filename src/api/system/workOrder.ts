import request from '@/utils/request'
import type {
  WorkInboundCreateDto,
  WorkInboundPageData,
  WorkInboundPageParams,
  WorkOrderApprovalStatus,
  WorkOrderDashboardData,
  WorkOrderPageData,
  WorkOrderPageParams,
  WorkOrderRecord,
  WorkOrderSaveDto,
  WorkReportCreateDto,
  WorkReportRecord,
  WorkReportPageData,
  WorkReportPageParams,
  WorkInboundRecord,
} from '@/types/system/workOrder'

export const pageWorkOrderApi = (params: WorkOrderPageParams) =>
  request.get<WorkOrderPageData>('/local/work-orders/page', params)

export const exportWorkOrderApi = (params: { keyword?: string; status?: number }) =>
  request.get<Blob>('/local/work-orders/export', params, { responseType: 'blob' })

export const listWorkOrderApi = (status?: number) =>
  request.get<WorkOrderRecord[]>('/local/work-orders/list', { status: status ?? undefined })

export const getWorkOrderDetailApi = (id: string) =>
  request.get<WorkOrderRecord>(`/local/work-orders/${id}`)

export const createWorkOrderApi = (data: WorkOrderSaveDto) =>
  request.post<unknown>('/local/work-orders', data)

export const updateWorkOrderApi = (id: string, data: WorkOrderSaveDto) =>
  request.put<unknown>(`/local/work-orders/${id}`, data)

export const deleteWorkOrderApi = (id: string) =>
  request.delete<unknown>(`/local/work-orders/${id}`)

export const submitWorkOrderApi = (id: string) =>
  request.post<unknown>(`/local/work-orders/${id}/submit`)

export const approveWorkOrderApi = (id: string) =>
  request.post<unknown>(`/local/work-orders/${id}/approve`)

export const rejectWorkOrderApi = (id: string, remark?: string) =>
  request.post<unknown>(`/local/work-orders/${id}/reject`, null, {
    params: { remark: remark || '' },
  })

export const cancelWorkOrderApi = (id: string) =>
  request.post<unknown>(`/local/work-orders/${id}/cancel`)

export const getWorkOrderApprovalStatusApi = (id: string) =>
  request.get<WorkOrderApprovalStatus>(`/local/work-orders/${id}/approval-status`)

export const getWorkOrderDashboardApi = (params?: { days?: number }) =>
  request.get<WorkOrderDashboardData>('/local/work-orders/dashboard', params)

export const pageWorkReportApi = (params: WorkReportPageParams) =>
  request.get<WorkReportPageData>('/local/work-reports/page', params)

export const exportWorkReportApi = (params: { keyword?: string; workOrderId?: string }) =>
  request.get<Blob>('/local/work-reports/export', params, { responseType: 'blob' })

export const createWorkReportApi = (data: WorkReportCreateDto) =>
  request.post<unknown>('/local/work-reports', data)

export const pageWorkInboundApi = (params: WorkInboundPageParams) =>
  request.get<WorkInboundPageData>('/local/work-inbounds/page', params)

export const exportWorkInboundApi = (params: { keyword?: string; workOrderId?: string }) =>
  request.get<Blob>('/local/work-inbounds/export', params, { responseType: 'blob' })

export const createWorkInboundApi = (data: WorkInboundCreateDto) =>
  request.post<unknown>('/local/work-inbounds', data)

export type {
  WorkOrderRecord,
  WorkOrderSaveDto,
  WorkOrderApprovalStatus,
  WorkOrderDashboardData,
  WorkReportCreateDto,
  WorkReportRecord,
  WorkInboundCreateDto,
  WorkInboundRecord,
}
