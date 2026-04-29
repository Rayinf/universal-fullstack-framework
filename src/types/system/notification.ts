// 通知记录
export interface NotificationRecord {
  id: string
  userId: string
  title: string
  content: string
  type: number // 1=审批 2=预警 3=系统
  bizType: string // quotation / contract / work_order ...
  bizId: string
  isRead: number // 0=未读 1=已读
  createTime: string
}

// 通知分页查询参数
export interface NotificationPageParams {
  current: number
  size: number
  isRead?: string // '0' | '1' | ''
}

// 通知分页数据
export interface NotificationPageData {
  records: NotificationRecord[]
  total: number
  size: number
  current: number
  pages: number
}

// 未读计数
export interface UnreadCountData {
  count: number
}
