import request from '@/utils/request'
import type {
  QuotationApprovalStatus,
  QuotationDetail,
  QuotationPageData,
  QuotationPageParams,
  QuotationRecord,
  QuotationSaveDto,
} from '@/types/system/quotation'

export const pageQuotationApi = (params: QuotationPageParams) =>
  request.get<QuotationPageData>('/local/quotations/page', params)

export const getQuotationDetailApi = (id: string) =>
  request.get<QuotationDetail>(`/local/quotations/${id}`)

export const createQuotationApi = (data: QuotationSaveDto) =>
  request.post<{ id: string }>('/local/quotations', data)

export const updateQuotationApi = (id: string, data: QuotationSaveDto) =>
  request.put<unknown>(`/local/quotations/${id}`, data)

export const deleteQuotationApi = (id: string) => request.delete<unknown>(`/local/quotations/${id}`)

export const submitQuotationApi = (id: string) =>
  request.post<unknown>(`/local/quotations/${id}/submit`)

export const approveQuotationApi = (id: string) =>
  request.post<unknown>(`/local/quotations/${id}/approve`)

export const rejectQuotationApi = (id: string, remark?: string) =>
  request.post<unknown>(`/local/quotations/${id}/reject`, null, {
    params: { remark: remark || '' },
  })

export const cancelQuotationApi = (id: string) =>
  request.post<unknown>(`/local/quotations/${id}/cancel`)

export const getQuotationApprovalStatusApi = (id: string) =>
  request.get<QuotationApprovalStatus>(`/local/quotations/${id}/approval-status`)

export type { QuotationApprovalStatus, QuotationDetail, QuotationRecord, QuotationSaveDto }
