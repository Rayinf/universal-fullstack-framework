import request from '@/utils/request'
import type {
  PurchaseOrderApprovalStatus,
  PurchaseOrderPageData,
  PurchaseOrderPageParams,
  PurchaseOrderRecord,
  PurchaseOrderSaveDto,
} from '@/types/system/purchaseOrder'

export const pagePurchaseOrderApi = (params: PurchaseOrderPageParams) =>
  request.get<PurchaseOrderPageData>('/local/purchase-orders/page', params)

export const createPurchaseOrderApi = (data: PurchaseOrderSaveDto) =>
  request.post<unknown>('/local/purchase-orders', data)

export const updatePurchaseOrderApi = (id: string, data: PurchaseOrderSaveDto) =>
  request.put<unknown>(`/local/purchase-orders/${id}`, data)

export const deletePurchaseOrderApi = (id: string) =>
  request.delete<unknown>(`/local/purchase-orders/${id}`)

export const submitPurchaseOrderApi = (id: string) =>
  request.post<unknown>(`/local/purchase-orders/${id}/submit`)

export const approvePurchaseOrderApi = (id: string) =>
  request.post<unknown>(`/local/purchase-orders/${id}/approve`)

export const cancelPurchaseOrderApi = (id: string) =>
  request.post<unknown>(`/local/purchase-orders/${id}/cancel`)

export const getPurchaseOrderApprovalStatusApi = (id: string) =>
  request.get<PurchaseOrderApprovalStatus>(`/local/purchase-orders/${id}/approval-status`)

export type { PurchaseOrderApprovalStatus, PurchaseOrderRecord, PurchaseOrderSaveDto }
