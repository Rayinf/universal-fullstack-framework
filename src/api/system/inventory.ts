import request from '@/utils/request'
import type {
  InventoryItemPageData,
  InventoryItemPageParams,
  InventoryItemRecord,
  InventoryItemSaveDto,
  InventoryTransactionCreateDto,
  InventoryTransactionPageData,
  InventoryTransactionPageParams,
  InventoryTransactionRecord,
} from '@/types/system/inventory'

export const pageInventoryItemApi = (params: InventoryItemPageParams) =>
  request.get<InventoryItemPageData>('/local/inventory/items/page', params)

export const createInventoryItemApi = (data: InventoryItemSaveDto) =>
  request.post<unknown>('/local/inventory/items', data)

export const updateInventoryItemApi = (id: string, data: InventoryItemSaveDto) =>
  request.put<unknown>(`/local/inventory/items/${id}`, data)

export const deleteInventoryItemApi = (id: string) =>
  request.delete<unknown>(`/local/inventory/items/${id}`)

export const getInventorySummaryApi = (params?: { keyword?: string; lowStockOnly?: number }) =>
  request.get<InventoryItemRecord[]>('/local/inventory/summary', params)

export const pageInventoryTransactionApi = (params: InventoryTransactionPageParams) =>
  request.get<InventoryTransactionPageData>('/local/inventory/transactions/page', params)

export const createInventoryTransactionApi = (data: InventoryTransactionCreateDto) =>
  request.post<unknown>('/local/inventory/transactions', data)

export type { InventoryItemRecord, InventoryTransactionRecord }
