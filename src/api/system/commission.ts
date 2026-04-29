import request from '@/utils/request'
import type {
  CommissionCalculateDto,
  CommissionPageData,
  CommissionPageParams,
  CommissionRecord,
  CommissionSummaryRecord,
} from '@/types/system/commission'

export const pageCommissionApi = (params: CommissionPageParams) =>
  request.get<CommissionPageData>('/local/commissions/page', params)

export const calculateCommissionApi = (contractId: string, data: CommissionCalculateDto) =>
  request.post<{ commissionAmount: number }>(`/local/commissions/calculate/${contractId}`, data)

export const payCommissionApi = (id: string, payDate?: string) =>
  request.post<unknown>(`/local/commissions/${id}/pay`, null, {
    params: { payDate: payDate || '' },
  })

export const deleteCommissionApi = (id: string) =>
  request.delete<unknown>(`/local/commissions/${id}`)

export const getCommissionSummaryApi = () =>
  request.get<CommissionSummaryRecord[]>('/local/commissions/summary')

export type { CommissionCalculateDto, CommissionRecord, CommissionSummaryRecord }
