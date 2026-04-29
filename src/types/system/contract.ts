export interface ContractRecord {
  id: string
  contractNo: string
  quotationId: string
  customerId: string
  customerName: string
  contractName: string
  totalAmount: number
  paidAmount: number
  signedDate: string
  startDate: string
  endDate: string
  paymentTerms: string
  status: number
  expireWarningSent: number
  remark: string
  createTime: string
  updateTime: string
}

export interface ContractPageParams {
  current: number
  size: number
  keyword?: string
  status?: number
}

export interface ContractPageData {
  records: ContractRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface ContractSaveDto {
  contractNo?: string
  quotationId?: string
  customerId: string
  customerName: string
  contractName: string
  totalAmount: number
  signedDate: string
  startDate: string
  endDate: string
  paymentTerms: string
  status: number
  remark: string
}

export interface ContractPaymentSummary {
  contractId: string
  contractNo: string
  customerName: string
  totalAmount: number
  paidAmount: number
  paidRate: number
}

export interface ContractDashboardData {
  cards: {
    pendingApprovalCount: number
    contractTotalAmount: number
    overallPaidRate: number
    expiringContractCount: number
    quotationConversionRate: number
  }
  paymentTrend: Array<{ month: string; amount: number }>
  customerContributionTop: Array<{ customerName: string; amount: number }>
  commissionTop: Array<{ salespersonName: string; amount: number }>
}
