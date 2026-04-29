export interface CommissionRecord {
  id: string
  contractId: string
  contractNo: string
  customerName: string
  salespersonId: string
  salespersonName: string
  contractAmount: number
  paymentAmount: number
  commissionRate: number
  commissionAmount: number
  status: number
  payDate: string
  remark: string
  createTime: string
}

export interface CommissionPageParams {
  current: number
  size: number
  status?: number
  salespersonName?: string
}

export interface CommissionPageData {
  records: CommissionRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface CommissionCalculateDto {
  salespersonId: string
  salespersonName: string
  commissionRate: number
  remark: string
}

export interface CommissionSummaryRecord {
  salespersonName: string
  recordCount: number
  totalCommission: number
  paidCommission: number
  pendingCommission: number
}
