export interface InventoryItemRecord {
  id: string
  sku: string
  itemName: string
  unit: string
  stockQty: number
  safetyQty: number
  isLowStock: boolean
  createTime: string
  updateTime: string
}

export interface InventoryItemPageParams {
  current: number
  size: number
  keyword?: string
}

export interface InventoryItemPageData {
  records: InventoryItemRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface InventoryItemSaveDto {
  sku: string
  itemName: string
  unit: string
  stockQty: number
  safetyQty: number
}

export interface InventoryTransactionRecord {
  id: string
  itemId: string
  sku: string
  itemName: string
  direction: number
  quantity: number
  afterStock: number
  businessNo: string
  operatorName: string
  remark: string
  createTime: string
}

export interface InventoryTransactionPageParams {
  current: number
  size: number
  keyword?: string
  direction?: number
}

export interface InventoryTransactionPageData {
  records: InventoryTransactionRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface InventoryTransactionCreateDto {
  itemId?: string
  sku?: string
  direction: number
  quantity: number
  businessNo: string
  operatorName: string
  remark: string
}
