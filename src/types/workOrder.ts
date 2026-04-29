// 生产工单相关类型定义

// 工单状态枚举
export type WorkOrderStatus =
  | '待派发'
  | '已派发'
  | '待执行'
  | '执行中'
  | '已完成'
  | '已合并'
  | '已拆分'
  | '已转线'
  | '已变更'
  | '已关闭'

// 工单变更类型
export type WorkOrderChangeType = 'merge' | 'split' | 'transfer'

// 工单优先级
export type WorkOrderPriority = '高' | '中' | '低' | '紧急插单'

// 标准API响应格式
export interface ApiResponse<T = any> {
  code: number
  msg: string | null
  data: T
}

// 分页响应格式
export interface PageResponse<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

// 生产工单基础信息
export interface WorkOrder {
  id: string
  workOrderCode: string
  parentTaskId: string
  parentTaskCode: string
  planId: string
  planCode: string
  productId: string
  productModel: string
  productName: string
  processId: string
  processCode: string
  processName: string
  processSequence: number
  isKeyProcess: boolean
  processFileId: string
  processFileName: string
  processFileVersion: string
  planQuantity: number
  completedQuantity: number
  qualifiedQuantity: number
  unqualifiedQuantity: number
  reworkQuantity: number
  status: WorkOrderStatus
  productionLineId: string
  productionLine: string
  workTeamId: string
  workTeam: string
  workstationId: string
  workstation: string
  planStartTime: string
  planEndTime: string
  actualStartTime: string
  actualEndTime: string
  onlineOperatorId: string
  onlineOperator: string
  offlineOperatorId: string
  offlineOperator: string
  changeType: WorkOrderChangeType | null
  changeReason: string
  originalWorkOrderId: string
  createdBy: string
  createdByName: string
  createdAt: string
  updatedBy: string
  updatedByName: string
  updatedAt: string
}

// 工单变更记录
export interface WorkOrderChange {
  id: string
  workOrderId: string
  workOrderCode: string
  changeType: WorkOrderChangeType
  beforeData: string
  afterData: string
  reason: string
  operatorId: string
  operatorName: string
  createdAt: string
}

// 工单关联关系
export interface WorkOrderRelation {
  id: string
  sourceWorkOrderId: string
  sourceWorkOrderCode: string
  targetWorkOrderId: string
  targetWorkOrderCode: string
  relationType: 'merged_from' | 'split_from' | 'transferred_from'
  createdAt: string
}

// 工序报工记录
export interface ProcessReport {
  id: string
  workOrderId: string
  workOrderCode: string
  processCode: string
  processName: string
  reportQuantity: number
  qualifiedQuantity: number
  unqualifiedQuantity: number
  reworkQuantity: number
  unqualifiedReasons: string[]
  reportMethod: 'batch' | 'piece'
  remarks: string
  operatorId: string
  operatorName: string
  reportTime: string
  createdAt: string
}

// 工单操作历史
export interface WorkOrderHistory {
  id: string
  workOrderId: string
  workOrderCode: string
  action: string
  actionDescription: string
  beforeStatus: string
  afterStatus: string
  operatorId: string
  operatorName: string
  operatorTime: string
  ipAddress: string
  remarks: string
  createdAt: string
}

// 生产计划
export interface ProductionPlan {
  id: string
  planCode: string
  taskId: string
  taskCode: string
  productId: string
  productModel: string
  productName: string
  planQuantity: number
  productionLineId: string
  productionLine: string
  planStartTime: string
  planEndTime: string
  status: '待生成' | '已生成' | '已发布' | '工单已生成' | '执行中' | '已完成'
  hasValidProcessRoute: boolean
  createdBy: string
  createdAt: string
}

// 工艺路线
export interface ProcessRoute {
  id: string
  productId: string
  productModel: string
  version: string
  status: '草稿' | '已发布' | '历史'
  processes: ProcessRouteItem[]
  createdBy: string
  createdAt: string
  publishedBy: string
  publishedAt: string
}

export interface ProcessRouteItem {
  id: string
  processId: string
  processCode: string
  processName: string
  sequence: number
  isKeyProcess: boolean
  processFileId: string
  processFileName: string
  processFileVersion: string
  standardWorkHours: number
}

// 生产资源
export interface ProductionResource {
  id: string
  resourceType: 'productionLine' | 'workTeam' | 'workstation'
  resourceCode: string
  resourceName: string
  parentId: string
  parentName: string
  status: 'available' | 'maintenance' | 'disabled'
  capacity: number
  calendarId: string
  managerId: string
  managerName: string
  createdAt: string
}

// 资源可用时间
export interface ResourceAvailableTime {
  resourceId: string
  resourceType: string
  date: string
  startTime: string
  endTime: string
  available: boolean
}

// 请求参数类型
export interface GenerateWorkOrderRequest {
  planIds: string[]
  operatorId: string
  operatorName: string
}

export interface DispatchWorkOrderRequest {
  workOrderIds: string[]
  resourceId: string
  resourceType: 'productionLine' | 'workTeam' | 'workstation'
  planStartTime: string
  planEndTime: string
  operatorId: string
  operatorName: string
}

export interface ChangeWorkOrderRequest {
  workOrderId: string
  changeType: WorkOrderChangeType
  reason: string
  operatorId: string
  operatorName: string
  targetWorkOrderIds?: string[]
  mergedQuantity?: number
  splitDetails?: { quantity: number; resourceId?: string }[]
  targetResourceId: string
  targetResourceType: 'productionLine' | 'workTeam' | 'workstation'
  newStartTime?: string
  newEndTime?: string
}

export interface OnlineConfirmRequest {
  workOrderId: string
  materialReady: boolean
  documentReady: boolean
  operatorId: string
  operatorName: string
}

export interface OfflineConfirmRequest {
  workOrderId: string
  finalQuantity: number
  finalQualified: number
  finalUnqualified: number
  operatorId: string
  operatorName: string
  remarks?: string
}

// 校验结果类型
export interface ValidationResult {
  valid: boolean
  errors?: string[]
  conflicts?: Array<{
    workOrderId: string
    workOrderCode: string
    reason: string
  }>
}
