// 基础信息维护相关类型定义

export interface BasicInfoRecord {
  id: number
  name: string
  type: number
  parentId?: number
  typeName?: string
  createTime?: string
  updateTime?: string
  delFlag?: string
}

export interface BasicInfoDto {
  id?: number
  name: string
  type: number
  parentId?: number
}

export interface BasicInfoPageQuery {
  id?: number
  keyWord?: string
  type?: number
  startDate?: string
  endDate?: string
  sortColumn?: string // 默认 create_time
  sortType?: 'asc' | 'desc'
}

export interface BasicInfoPageRequest {
  records?: any[]
  total?: number
  size: number
  current: number
  optimizeJoinOfCountSql?: boolean
  pages?: number
}

export interface BasicInfoIPage<T> {
  size: number
  total: number
  pages: number
  current: number
  records: T[]
}

export interface BasicInfoApiResponse<T> {
  code: number
  msg: string | null
  data?: T  // data字段可选，因为后端可能不返回data
}

// 仅用于前端 mock 的简化类型定义
export type BasicInfoType =
  | 'company'
  | 'projectProgress'
  | 'salesperson'
  | 'category'
  | 'shipmentType'
  | 'receiveType'
  | 'customerLevel'

export interface BasicInfoItem {
  id: string
  name: string
  createdAt?: string
  updatedAt?: string
}

export interface BasicInfoQuery {
  name?: string
}