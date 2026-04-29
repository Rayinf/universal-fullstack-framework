/**
 * 计划排程管理类型定义 (SRS-FUNC-0003)
 */

// 排程状态
export type ScheduleStatus = '待排程' | '已排程' | '审核中' | '审核通过' | '审核不通过' | '已派发' | '执行中' | '已完成' | '已取消'

// 审核状态
export type ApprovalStatus = '待审核' | '审核中' | '审核通过' | '审核不通过'

// 派发状态
export type DistributionStatus = '待派发' | '已派发'

// 执行状态
export type ExecutionStatus = '待执行' | '执行中' | '已完成'

// 生产排程/计划方案
export interface Schedule {
  id: string
  scheduleCode: string // 方案编号
  scheduleName: string // 方案名称
  taskIds: string[] // 关联任务ID列表
  productionLine?: string // 生产线
  planStartTime: string // 计划开始时间
  planEndTime: string // 计划结束时间
  status: ScheduleStatus // 方案状态
  approvalStatus?: ApprovalStatus // 审核状态
  distributionStatus?: DistributionStatus // 派发状态
  executionStatus?: ExecutionStatus // 执行状态
  
  // 审核相关
  approvers?: string[] // 审核人列表
  approvalTime?: string // 审核完成时间
  approvalRecords?: ApprovalRecord[] // 审核记录
  
  // 派发相关
  recipients?: string[] // 接收人/部门列表
  distributionTime?: string // 派发时间
  distributionNote?: string // 派发附言
  
  // 执行相关
  actualStartTime?: string // 实际开始时间
  actualEndTime?: string // 实际结束时间
  progress?: number // 执行进度百分比
  
  // 基础信息
  remarks?: string // 备注
  createdBy: string // 创建人
  createdAt: string // 创建时间
  updatedAt?: string // 更新时间
}

// 排程表单数据
export interface ScheduleFormData {
  scheduleName: string
  taskIds: string[]
  productionLine?: string
  planStartTime: string
  planEndTime: string
  remarks?: string
}

// 排程筛选参数
export interface ScheduleFilterParams {
  status?: ScheduleStatus | ''
  approvalStatus?: ApprovalStatus | ''
  distributionStatus?: DistributionStatus | ''
  executionStatus?: ExecutionStatus | ''
  productionLine?: string
  keyword?: string
  dateRange?: [string, string]
}

// 审核记录
export interface ApprovalRecord {
  id: string
  scheduleId: string
  approver: string // 审核人
  approverRole?: string // 审核人角色
  conclusion: '通过' | '不通过' // 审核结论
  opinion: string // 审核意见
  approvalTime: string // 审核时间
}

// 派发记录
export interface DistributionRecord {
  id: string
  scheduleId: string
  recipient: string // 接收人/部门
  recipientType: '部门' | '个人' // 接收方类型
  note?: string // 附言
  distributedBy: string // 派发人
  distributedAt: string // 派发时间
  status: '已接收' | '未接收' // 接收状态
}

// 执行任务
export interface ExecutionTask {
  id: string
  scheduleId: string
  taskId: string
  taskCode: string
  assignee: string // 责任人
  assigneeDept: string // 责任部门
  taskType: '生产执行' | '工艺准备' | '物料准备' | '质量检验' // 任务类型
  status: ExecutionStatus
  startTime?: string
  endTime?: string
  feedback?: string // 反馈信息
  createdAt: string
  updatedAt?: string
}
