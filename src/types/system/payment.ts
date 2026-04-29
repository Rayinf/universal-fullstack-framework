export interface PaymentRecord {
  id: string
  contractId: string
  paymentNo: string
  paymentAmount: number
  paymentDate: string
  paymentMethod: number
  payerName: string
  receivedBy: string
  remark: string
  status: number
  createTime: string
  contractNo: string
  customerName: string
}

export interface PaymentPageParams {
  current: number
  size: number
  contractId?: string
  status?: number
}

export interface PaymentPageData {
  records: PaymentRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface PaymentSaveDto {
  contractId: string
  paymentNo?: string
  paymentAmount: number
  paymentDate: string
  paymentMethod: number
  payerName: string
  receivedBy?: string
  remark: string
}
