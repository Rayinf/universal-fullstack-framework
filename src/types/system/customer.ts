export interface Customer {
  id: string
  customerCode: string
  customerName: string
  accountManagerName?: string
  introducerName?: string
  customerLevel?: number
  specialNotes?: string
  createBy?: string
  creator?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  isDeleted?: number
}

export interface CustomerPageQuery {
  customerCode?: string
  searchKey?: string
  customerLevel?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
}

export interface CustomerPageRequest {
  current: number
  size: number
}
