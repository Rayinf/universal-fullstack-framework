export interface PurchaseOrderRecord {
  id: string
  orderNo: string
  supplierName: string
  itemName: string
  quantity: number
  unitPrice: number
  totalAmount: number
  status: number
  applicant: string
  remark: string
  createTime: string
  updateTime: string
}

export interface PurchaseOrderPageParams {
  current: number
  size: number
  keyword?: string
  status?: number
}

export interface PurchaseOrderPageData {
  records: PurchaseOrderRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface PurchaseOrderSaveDto {
  orderNo: string
  supplierName: string
  itemName: string
  quantity: number
  unitPrice: number
  totalAmount: number
  status: number
  applicant: string
  remark: string
}

export interface PurchaseApprovalNodeStatus {
  nodeIndex: number
  nodeName: string
  nodeStatus: number // 0:待处理 1:待审批 2:已通过 4:已终止
  roleId?: string
  roleName?: string
  approvalIds?: string[]
  approvalPeopleName?: string[]
  approverId?: string
  approverName?: string
  action?: string
  actionTime?: string
}

export interface PurchaseOrderApprovalStatus {
  orderId: string
  orderNo: string
  orderStatus: number
  approvalFlowId: number
  currentNodeIndex: number
  nodes: PurchaseApprovalNodeStatus[]
}
