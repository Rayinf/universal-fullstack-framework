export interface QuotationItemRecord {
  id: string
  quotationId: string
  productId: string
  productCode: string
  productName: string
  specification: string
  unit: string
  quantity: number
  unitPrice: number
  amount: number
  sortOrder: number
  remark: string
}

export interface QuotationRecord {
  id: string
  quoteNo: string
  customerId: string
  customerName: string
  contactPerson: string
  totalAmount: number
  discountRate: number
  finalAmount: number
  validityDays: number
  validityEndDate: string
  status: number
  applicant: string
  approvalFlowId: number
  currentNodeIndex: number
  version: number
  remark: string
  createTime: string
  updateTime: string
}

export interface QuotationDetail extends QuotationRecord {
  items: QuotationItemRecord[]
}

export interface QuotationPageParams {
  current: number
  size: number
  keyword?: string
  status?: number
}

export interface QuotationPageData {
  records: QuotationRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface QuotationNodeStatus {
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

export interface QuotationApprovalStatus {
  quotationId: string
  quoteNo: string
  quotationStatus: number
  approvalFlowId: number
  currentNodeIndex: number
  nodes: QuotationNodeStatus[]
}

export interface QuotationSaveDto {
  quoteNo?: string
  customerId: string
  customerName: string
  contactPerson: string
  discountRate: number
  validityDays: number
  validityEndDate: string
  status: number
  applicant: string
  version: number
  remark: string
  items: Array<{
    productId?: string
    productCode: string
    productName: string
    specification: string
    unit: string
    quantity: number
    unitPrice: number
    amount?: number
    sortOrder?: number
    remark?: string
  }>
}
