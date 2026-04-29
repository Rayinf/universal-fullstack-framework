export interface WorkOrderRecord {
  id: string
  workOrderNo: string
  contractId: string
  contractNo: string
  customerName: string
  productId: string
  productCode: string
  productName: string
  planQuantity: number
  reportedQuantity: number
  qualifiedQuantity: number
  inboundQuantity: number
  status: number
  priority: number
  plannedStartDate: string
  plannedEndDate: string
  actualStartTime: string
  actualEndTime: string
  applicant: string
  approvalFlowId: number
  currentNodeIndex: number
  remark: string
  createTime: string
  updateTime: string
}

export interface WorkOrderPageParams {
  current: number
  size: number
  keyword?: string
  status?: number
}

export interface WorkOrderPageData {
  records: WorkOrderRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface WorkOrderSaveDto {
  workOrderNo?: string
  contractId: string
  contractNo: string
  customerName: string
  productId: string
  productCode: string
  productName: string
  planQuantity: number
  status: number
  priority: number
  plannedStartDate: string
  plannedEndDate: string
  applicant: string
  remark: string
}

export interface WorkOrderApprovalNode {
  nodeIndex: number
  nodeName: string
  nodeStatus: number
  roleId: string
  roleName: string
  approvalIds: string[]
  approvalPeopleName: string[]
  approverId: string
  approverName: string
  action: string
  actionTime: string
}

export interface WorkOrderApprovalStatus {
  workOrderId: string
  workOrderNo: string
  workOrderStatus: number
  approvalFlowId: number
  currentNodeIndex: number
  nodes: WorkOrderApprovalNode[]
}

export interface WorkReportRecord {
  id: string
  workOrderId: string
  workOrderNo: string
  processName: string
  reportQuantity: number
  qualifiedQuantity: number
  defectQuantity: number
  reportUserId: string
  reportUserName: string
  reportTime: string
  remark: string
  createTime: string
  productName: string
  customerName: string
}

export interface WorkReportPageParams {
  current: number
  size: number
  keyword?: string
  workOrderId?: string
}

export interface WorkReportPageData {
  records: WorkReportRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface WorkReportCreateDto {
  workOrderId: string
  processName: string
  reportQuantity: number
  qualifiedQuantity: number
  defectQuantity: number
  reportTime: string
  remark: string
}

export interface WorkInboundRecord {
  id: string
  inboundNo: string
  workOrderId: string
  workOrderNo: string
  quantity: number
  warehouseName: string
  operatorName: string
  inboundTime: string
  remark: string
  createTime: string
  productName: string
  customerName: string
}

export interface WorkInboundPageParams {
  current: number
  size: number
  keyword?: string
  workOrderId?: string
}

export interface WorkInboundPageData {
  records: WorkInboundRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface WorkInboundCreateDto {
  workOrderId: string
  inboundNo?: string
  quantity: number
  warehouseName: string
  inboundTime: string
  remark: string
}

export interface WorkOrderDashboardData {
  cards: {
    totalCount: number
    pendingApprovalCount: number
    producingCount: number
    pendingInboundCount: number
    completedCount: number
    completionRate: number
  }
  reportTrend: Array<{ date: string; quantity: number }>
  inboundTrend: Array<{ date: string; quantity: number }>
  statusDistribution: Array<{ status: number; statusName: string; count: number }>
  productTop: Array<{ productName: string; quantity: number }>
}
