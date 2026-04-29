import request from '@/utils/request'
import type {
  PaymentPageData,
  PaymentPageParams,
  PaymentRecord,
  PaymentSaveDto,
} from '@/types/system/payment'

export const pagePaymentApi = (params: PaymentPageParams) =>
  request.get<PaymentPageData>('/local/payments/page', params)

export const createPaymentApi = (data: PaymentSaveDto) =>
  request.post<unknown>('/local/payments', data)

export const confirmPaymentApi = (id: string) =>
  request.post<unknown>(`/local/payments/${id}/confirm`)

export const deletePaymentApi = (id: string) => request.delete<unknown>(`/local/payments/${id}`)

export type { PaymentRecord, PaymentSaveDto }
