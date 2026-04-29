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
  sortColumn?: string
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

export interface ScanBindingProcessRecord {
  id: number
  scanAssetNumber: string
  identifier: string
  processId: number
  processName?: string
  createTime?: string
  updateTime?: string
}

export interface ScanBindingProcessDto {
  id?: number
  scanAssetNumber: string
  identifier: string
  processId?: number
}

export interface BasicInfoApiResponse<T> {
  code: number
  msg: string | null
  data?: T
}

// 参数类型映射 (数字类型)
export const PARAM_TYPE_MAP = {
  COMPANY: 1, // 公司管理
  PROJECT_PROGRESS: 2, // 项目进度
  SALESPERSON: 3, // 销售人员
  CATEGORY: 4, // 品类管理
  SHIPMENT_TYPE: 5, // 发货类型
  RECEIVE_TYPE: 6, // 收货类型
  CUSTOMER_LEVEL: 7, // 客户等级
  PROCESS_STEP: 8, // 工序名称
  PROCESS_LIBRARY: 9, // 工艺要求库名称
  SCANNER_MAPPING: 10, // 扫描枪工序关联
  STORAGE_LOCATION: 11, // 存储位置
  LOGISTICS_COMPANY: 12, // 物流公司
  ASSET_TYPE: 13, // 资产类型
  EQUIPMENT_TYPE: 14, // 设备类型
  DEPARTMENT: 15, // 部门管理
  PRODUCT_TYPE: 99, // 产品类型
} as const

export type ParamTypeKey = keyof typeof PARAM_TYPE_MAP
