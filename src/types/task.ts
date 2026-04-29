/**
 * 任务管理相关类型定义
 * 对应需求规格书 SRS-FUNC-0002
 * 对齐后端 orderInfo 接口
 */

export type TaskStatus =
  | '待核查'
  | '已核查'
  | '待排程'
  | '已排程'
  | '已排程（待审核）'
  | '已排程（已审核）'
  | '已派发'
  | '生产中'
  | '质检中'
  | '已完成'
  | '已交付'
  | '延迟'
  | '已提交至计划' // 兼容状态，对应状态3

export type TaskPriority = '高' | '中' | '低' | '紧急插单'

// 附件信息
export interface TaskAttachment {
  id: string
  originalFileName: string // 原始文件名
  fileName: string // MinIO 文件名
  suffixName: string // 后缀
  url?: string
  createTime: string
  creator: string
  orderId: string
  remarks?: string
}

// 任务修改历史记录（用于中转修改追溯）
export interface TaskModifyLog {
  id: string
  taskId: string
  fieldName: string
  oldValue: string
  newValue: string
  modifyTime: string
  modifyBy: string
  modifyType: '中转修改' | '常规修改'
}

// 任务工序进度节点
export interface TaskProgressNode {
  id: string
  nodeName: string
  nodeType: '任务录入' | '信息核查' | '任务提交' | '计划排程' | '生产执行' | '质量检验' | '任务完成'
  status: '未开始' | '进行中' | '已完成' | '已跳过'
  plannedTime?: string
  actualTime?: string
  operator?: string
  remarks?: string
}

export interface Task {
  id: string
  taskCode: string // orderNo
  taskName: string // orderName
  barcode?: string // barcode
  contractNo: string // contractNo
  customerId: string // customerId
  customerName: string // 关联展示字段
  productName: string // productName
  productNo: string // productNo
  productModel: string // orderModel
  plannedQuantity: number | undefined // productQuantity
  plannedDeliveryDate: string // deliveryTime
  priority: TaskPriority // priority (1-4)
  status: TaskStatus // progressStatus (1-12)
  taskType: number // 1: 生产任务, 2: 来料检验任务
  // 附件列表
  attachments?: TaskAttachment[]
  // 核查信息
  verifier?: string
  verificationTime?: string
  // 提交信息
  submitter?: string
  submissionTime?: string
  // 进度信息
  progress?: number
  progressNodes?: TaskProgressNode[]
  // 工序进度（用于展示工艺执行进度）
  processSteps?: Array<{ name: string; status: string; time: string }>
  // 修改历史 (对应后端 orderInfoHistoryDOList)
  orderInfoHistoryDOList?: any[]
  // 版本号
  version?: string
  // 实际执行时间
  actualStartTime?: string
  actualEndTime?: string
  // 其他
  remarks?: string
  processRouteId?: string // processRouteId
  createdAt: string // createTime
  createdBy: string // createBy
  updatedAt?: string
  updatedBy?: string
}

export interface TaskFormData {
  taskCode?: string // orderNo
  taskName: string // orderName
  contractNo: string
  customerId: string
  customerName: string
  productName: string
  productNo: string
  productModel: string
  plannedQuantity: number | undefined // productQuantity
  plannedDeliveryDate: string // deliveryTime
  priority: TaskPriority
  remarks?: string
  barcode?: string
  attachments?: TaskAttachment[]
}

// 中转修改表单（仅允许修改特定字段）
export interface TaskTransferModifyData {
  plannedDeliveryDate?: string
  priority?: TaskPriority
  remarks?: string
}

export interface TaskFilterParams {
  status?: TaskStatus
  priority?: TaskPriority
  customerName?: string
  productModel?: string
  contractNo?: string
  taskCode?: string
  // 日期范围筛选
  deliveryDateRange?: [string, string]
  createDateRange?: [string, string]
  keyword?: string
}

// 筛选选项（用于下拉框）
export interface TaskFilterOptions {
  customers: string[]
  productModels: string[]
  priorities: TaskPriority[]
  statuses: TaskStatus[]
}
