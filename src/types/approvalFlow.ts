import type { ApiResponse as BaseApiResponse } from '@/utils/request'

/**
 * 审批规则主表
 */
export interface ApprovalFlow {
  id?: number
  approvalFlowName: string // 审批规则名称
  processLibraryId?: number // 业务模块（工艺库ID，仅当approvalType=1时使用）
  processLibraryName?: string // 工艺库名称（仅用于显示）
  approvalType: 1 | 2 | 3 | 4 | 5 // 审批规则类型 1：工艺库 2：排程 3：采购订单 4：报价单 5：生产工单
  status: 1 | 2 // 状态 1：启用 2：未启用
  remarks?: string // 备注信息
  createBy?: number
  creator?: string // 创建人名称
  createTime?: string
  updateBy?: number
  updateTime?: string
  isDeleted?: number
}

/**
 * 审批流程节点信息
 */
export interface ApprovalFlowNode {
  id?: number
  approvalFlowId?: number // 审核规则id
  approvalNodeName: string // 审批节点名称
  roleId?: number // 审核节点指定的角色id
  roleName?: string // 审核节点指定的角色名称（显示用）
  approvalIds?: string // 审批人，逗号拼接的字符串
  approvalPeopleName?: string[] // 审批人名称列表（显示用）
  nodeIndex: number // 审批节点的顺序
  remarks?: string // 审批节点备注信息
  createBy?: number
  createTime?: string
  updateBy?: number
  updateTime?: string
  isDeleted?: number
}

/**
 * 审批流程详情信息（含节点）
 */
export interface ApprovalFlowDetail {
  id: number
  approvalFlowName: string // 审批规则名称
  approvalFlowId: number // 审核规则主表Id
  processLibraryId?: number // 业务模块
  processLibraryName?: string // 业务工序节点名称
  status: 1 | 2 // 状态 1：启用 2：未启用
  processFlowRemarks?: string // 工艺节点下属业务备注信息
  approvalNodeName: string // 审批节点名称
  roleId?: number // 审核节点指定的角色id
  roleName?: string // 审核节点指定的角色名称
  approvalIds?: string // 审批人，逗号拼接的字符串
  approvalPeopleName?: string[] // 审批人名称列表
  nodeIndex: number // 审批节点的顺序
  remarks?: string // 审批节点备注信息
}

/**
 * 审批规则分页查询参数
 */
export interface ApprovalFlowPageQuery {
  keyword?: string // 关键词（规则名称）
  status?: 1 | 2 // 状态
  approvalType?: 1 | 2 | 3 | 4 | 5 // 审批规则类型
  startDate?: string // 创建开始日期
  endDate?: string // 创建结束日期
  sortColumn?: string // 排序列
  sortType?: 'asc' | 'desc' // 排序方式
}

/**
 * 分页请求参数
 */
export interface PageRequest {
  records?: any[]
  total?: number
  size: number
  current: number
  optimizeJoinOfCountSql?: boolean
  pages?: number
}

/**
 * 分页响应数据
 */
export interface IPage<T> {
  size: number
  total: number
  pages: number
  current: number
  records: T[]
}

/**
 * API响应格式
 */
export type ApiResponse<T> = BaseApiResponse<T>

/**
 * 审批规则保存DTO（新增）
 */
export interface ApprovalFlowSaveDTO {
  approvalFlowName: string
  processLibraryId?: number
  approvalType: 1 | 2 | 3 | 4 | 5
  status: 1 | 2
  remarks?: string
}

/**
 * 审批规则更新DTO（编辑）
 */
export interface ApprovalFlowUpdateDTO extends ApprovalFlowSaveDTO {
  id: number
}

/**
 * 审批节点保存DTO
 */
export interface ApprovalFlowNodeSaveDTO {
  id?: number
  approvalFlowId: number
  approvalNodeName: string
  roleId?: number
  approvalIds?: string
  nodeIndex: number
  remarks?: string
}

/**
 * 审批结果分页查询参数
 */
export interface ApprovalFlowResultQuery {
  keyword?: string
  processPeopleId?: string | number
  orderId?: string | number
  orderSchedulingId?: string | number
  processLibraryId?: string | number
  approvalFlowId?: string | number
  approvalStatus?: number // 1：通过 2：不通过 3：待审批
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: 'asc' | 'desc'
}

/**
 * 审批结果VO
 */
export interface ApprovalFlowResultVO {
  id: string | number
  orderId: string | number
  resultType: 1 | 2 | 3 // 1：工艺库 2：排程 3：采购订单
  orderSchedulingId: string | number
  orderName: string
  productName: string
  processLibraryId: string | number
  processLibraryName: string
  approvalFlowId: string | number
  approvalFlowName: string
  processPeople: string | number
  processPeopleName: string
  approvalStatus: 1 | 2 | 3 // 1：通过 2：不通过 3：待审批
  approvalRemarks: string
  createBy: string | number
  creator: string
  createTime: string
}
