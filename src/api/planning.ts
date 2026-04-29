import request from '@/utils/request'

/**
 * 计划排程管理 API
 */

// --- 接口定义 ---

// IPage 响应结构
export interface IPage<T> {
  size: number
  total: number
  records: T[]
  current: number
  pages: number
}

// 基础分页请求参数
export interface PageParams {
  current?: number
  size?: number
}

/**
 * 工单排程编辑DTO类
 */
export interface OrderSchedulingUpdateDTO {
  id?: string // 主键id
  orderId?: string // 工单id
  schedulingName?: string // 排程方案名称
  schedulingStartTime?: string // 排程计划开始时间
  schedulingEndTime?: string // 排程计划结束时间
  remarks?: string // 排程方案备注信息
  reviewStatus?: number // 1: 待审核 2：审核中 3：审核通过 4：审核不通过 5：派发中 6：待派发 7:工单已生成
  reviewCompletedTime?: string // 审核通过时间
  createBy?: string // 创建人
  createTime?: string // 创建时间
  updateBy?: string // 更新人
  updateTime?: string // 更新时间
  isDeleted?: number // 是否删除:1-是,0-否
}

/**
 * 工单排程任务派发保存DTO类
 */
export interface OrderSchedulingDistributeSaveDTO {
  id?: string // 主键id
  orderId?: string // 工单id
  schedulingId?: string // 排程方案id
  deptId?: string // 负责部门id
  director?: string // 负责人id
  status?: number // 执行状态 1：待执行 2：已完成
  remarks?: string // 排程方案背景说明
  createBy?: string // 创建人
  createTime?: string // 创建时间
  updateBy?: string // 更新人
  updateTime?: string // 更新时间
  isDeleted?: number // 是否删除:1-是,0-否
}

/**
 * 工单排程任务派发新增DTO类
 */
export interface OrderSchedulingDistributeDTO {
  orderSchedulingDistributeSaveDTOList: OrderSchedulingDistributeSaveDTO[]
  schedulingId: string // 排程方案id
}

/**
 * 订单信息表 (VO)
 */
export interface OrderInfoVO {
  orderScheduledId?: string // 新增：排程关联ID
  id: string // 主键id
  orderNo: string // 工单编号
  orderName: string // 工单名称
  productName?: string // 产品名称
  productNo?: string // 产品编号
  processRouteId?: string // 工艺路线Id
  barcode?: string // 工单的条形码内容
  productQuantity?: number // 工单的生成数量
  version?: string // 工单版本
  orderModel?: string // 产品型号
  customerId?: string // 客户表id
  progressStatus?: number // 工单状态
  deliveryTime?: string // 交货时间
  contractNo?: string // 合同编号
  taskType?: number // 任务类型
  remarks?: string // 工单备注信息
  createBy?: string // 创建人
  creator?: string // 创建人名称
  createTime?: string // 创建时间
  updateBy?: string // 更新人
  updateTime?: string // 更新时间
  isDeleted?: number // 是否删除
  priority?: number // 工单优先级
}

/**
 * 工单排程表VO类
 */
export interface OrderSchedulingVO {
  orderScheduledId?: string // 新增：工单排程ID，用于更新
  id: string // 主键id (工单ID)
  orderId: string // 工单id (通常与 id 相同，或为对象)
  productName?: string // 产品名称
  productNo?: string // 产品编号
  schedulingName: string // 排程方案名称
  schedulingStartTime?: string // 排程计划开始时间
  schedulingEndTime?: string // 排程计划结束时间
  remarks?: string // 排程方案备注信息
  reviewStatus?: number // 1: 待审核 2：审核中 3：审核通过 4：审核不通过 5：已派发 6:工单已生成
  reviewCompletedTime?: string // 审核通过时间
  createBy?: string // 创建人
  creator?: string // 创建人名称
  createTime?: string // 创建时间
  updateBy?: string // 更新人
  updateTime?: string // 更新时间
  isDeleted?: number // 是否删除:1-是,0-否
}

/**
 * 待执行列表 (VO)
 */
export interface ExecutionTaskVO {
  id: string // 订单id 或 分配记录id
  orderSchedulingDistributeId?: string // 派发记录ID
  orderId?: string // 关联的工单ID (如果是分配记录ID为主键)
  orderNo: string // 工单编号
  orderName: string // 工单名称
  productName?: string // 产品名称
  productNo?: string // 产品编号
  deptName?: string // 部门名称
  productQuantity?: number // 工单生产的数量
  schedulingName?: string // 排程方案名称
  orderSchedulingId?: string // ⭐ 排程方案ID
  schedulingStartTime?: string // 排程计划开始时间
  schedulingEndTime?: string // 排程计划结束时间
  reviewStatus?: number // 状态
}

/**
 * 任务执行详情VO
 */
export interface ExecutionDetailVO {
  orderInfoList: OrderInfoVO[] // 任务表信息
  orderSchedulingList: OrderSchedulingVO[] // 排程表信息
}

/**
 * 查询待排程任务 DTO
 */
export interface OrderSchedulingQueryDTO {
  id?: string
  orderNo?: string
  deliveryTime?: string
  contractNo?: string
  keyword?: string
  taskType?: number
  progressStatus?: number
  priority?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
}

/**
 * 查询待转发生产计划 DTO
 */
export interface OrderSchedulingForwardQueryDTO {
  orderModel?: string
  keyword?: string
  reviewStatus?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
}

/**
 * 查看待执行任务 DTO
 */
export interface OrderSchedulingExecuteQueryDTO {
  orderId?: string
  keyword?: string
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
}

// --- API 请求函数 ---

/**
 * 工单排程编辑
 */
export const updateOrderScheduling = (data: OrderSchedulingUpdateDTO) =>
  request.post<unknown>('/manage/api/orderInfoScheduling/updateOrderScheduling', data)

/**
 * 生产计划派发
 */
export const distribute = (data: OrderSchedulingDistributeDTO) =>
  request.post<unknown>('/manage/api/orderInfoScheduling/distribute', data)

/**
 * 计划执行确认完工
 */
export const confirmCompletion = (data: OrderSchedulingDistributeSaveDTO) =>
  request.post<unknown>('/manage/api/orderInfoScheduling/confirmCompletion', data)

/**
 * 通过ID查询待排程任务详情信息
 */
export const getPendingTaskDetail = (id: string) =>
  request.get<OrderInfoVO>(`/manage/api/orderInfoScheduling/${id}`)

/**
 * 分页查询待排程任务信息
 */
export const getPendingTaskPage = (params: PageParams & OrderSchedulingQueryDTO) =>
  request.get<IPage<OrderInfoVO>>('/manage/api/orderInfoScheduling/page', params)

/**
 * 获取已排程列表信息 (POST请求)
 * 注意：虽然是POST请求，但后端返回的是数组格式，不是分页格式
 */
export const getAlreadyScheduledList = (data: PageParams & OrderSchedulingForwardQueryDTO) =>
  request.post<OrderSchedulingVO[]>(
    '/manage/api/orderInfoScheduling/getAlreadyScheduledList',
    data,
  )

/**
 * 通过订单ID查询待转发生产计划详情信息
 */
export const getForwardDetail = (id: string) =>
  request.get<OrderInfoVO>(`/manage/api/orderInfoScheduling/forward/${id}`)

/**
 * 分页查看待执行任务信息
 */
export const getExecutePage = (params: PageParams & OrderSchedulingExecuteQueryDTO) =>
  request.get<IPage<ExecutionTaskVO>>('/manage/api/orderInfoScheduling/executePage', params)

/**
 * 分页查看待执行任务执行列表信息
 */
export const getExecuteList = (params: PageParams & OrderSchedulingExecuteQueryDTO) =>
  request.get<IPage<any>>('/manage/api/orderInfoScheduling/executeList', params)

/**
 * 查看待执行任务信息详情
 */
export const getExecuteDetail = (id: string) =>
  request.get<ExecutionDetailVO>(`/manage/api/orderInfoScheduling/executePage/${id}`)

/**
 * 提交排程方案审核
 */
export const saveApprovalInfo = (schedulingId: string | number) =>
  request.get<unknown>('/manage/api/orderInfoScheduling/saveApprovalInfo', { schedulingId })

/**
 * 审批流程结果信息新增DTO类
 */
export interface ApprovalResultSaveDTO {
  id?: string // 主键id
  orderId?: string // 任务订单id
  orderSchedulingId?: string // 排程信息id
  processLibraryId?: string // 工序节点id
  approvalFlowId?: string // 审批流程主表id
  approvalFlowNodeInfoId?: string // 审批流程节点表id
  processPeople?: string // 审批人
  approvalStatus?: number // 审批结果 1：通过 2：不通过 3：待审批
  approvalRemarks?: string // 审批描述信息
  createBy?: string // 创建人
  createTime?: string // 创建时间
  updateBy?: string // 更新人
  updateTime?: string // 更新时间
  isDeleted?: number // 是否删除:1-是,0-否
}

/**
 * 保存审批人审批结果信息
 */
export const saveApprovalResult = (data: ApprovalResultSaveDTO) =>
  request.post<unknown>('/manage/api/approvalFlowResult/saveApprovalResult', data)

/**
 * 获取当前用户对排程信息需审核信息
 */
export const getOrderSchedulingResult = (orderSchedulingId: string | number) =>
  request.get<any>('/manage/api/approvalFlowResult/getOrderSchedulingResult', { orderSchedulingId })

/**
 * 获取对应排程信息的所有审核信息
 */
export const getOrderSchedulingResultForAll = (orderSchedulingId: string | number) =>
  request.get<any[]>('/manage/api/approvalFlowResult/getOrderSchedulingResultForAll', {
    orderSchedulingId,
  })

/**
 * 获取当前用户已排程列表（需审核列表）
 */
export const getAlreadyScheduledListForCurrentUser = (params?: any) =>
  request.get<any[]>(
    '/manage/api/orderInfoScheduling/getAlreadyScheduledListForCurrentUser',
    params,
  )
