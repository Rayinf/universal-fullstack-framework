import request from '@/utils/request'

// 工单明细信息表VO类
export interface WorkOrderDetailVO {
  id: string
  workOrderNo: string
  workQuantity: number
  orderId: string
  orderName: string
  processRouteId: string
  processRouteName: string
  orderSchedulingId: string
  orderSchedulingName: string
  workOrderId: string
  productName?: string
  productModel?: string
  status: number // 1：待派发 2：已派发 3:执行中 4：已完成
  orderWordType: number // 1：未变更 2：已变更 3：变更衍生 4：转线
  processLibraryId?: string
  processLibraryName?: string
  workStartTime?: string
  workEndTime?: string
  producedQuantity?: number
  qualifiedQuantity?: number
  unqualifiedQuantity?: number
  reworkQuantity?: number
  actualStartTime?: string
  actualEndTime?: string
  onlineOperator?: string
  offlineOperator?: string
  createBy?: string
  creator?: string
  createTime?: string
  isDeleted?: number
  deptId?: string // 部门ID
}

// 分页查询DTO
export interface WorkOrderDetailPageDTO {
  keyword?: string
  status?: number
  orderWordType?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
  current?: number
  size?: number
}

// 工单派发信息新增DTO类 (只保留要求的4个字段，其他根据需要可选)
export interface OrderWorkDetailSaveDTO {
  workOrderDetailId?: string // 对应 page 的 id
  deptId?: string // 负责部门id
  workStartTime?: string // 计划开始时间
  workEndTime?: string // 计划结束时间
  [key: string]: any // 允许其他字段，但主要关注上述字段
}

// 变更/派发保存DTO
export interface OrderWorkDetailChangeDTO {
  orderWorkDetailSaveDTOUpdate?: OrderWorkDetailSaveDTO | null
  orderWorkDetailSaveDTOUpdateAdd?: OrderWorkDetailSaveDTO | null
  orderWorkDetailSaveDTOList?: OrderWorkDetailSaveDTO[] // 增加对列表的支持
  changeReason?: string // 变更原因
  changeType?: 'merge' | 'split' | 'transfer' // 变更类型
}

// 工单报工DTO
export interface OrderWorkReportDTO {
  workOrderDetailId: string | number
  qualifiedQuantity: number
  unqualifiedQuantity: number
  reworkQuantity: number
}

// 分页查询工单拆分明细列表
export const getWorkOrderDetailPage = (params: WorkOrderDetailPageDTO) => {
  return request.get<any>('/manage/api/orderWorkDetail/page', {
    current: params.current || 1,
    size: params.size || 10,
    keyword: params.keyword,
    status: params.status,
    orderWordType: params.orderWordType,
    startDate: params.startDate,
    endDate: params.endDate,
    sortColumn: params.sortColumn || 'create_time',
    sortType: params.sortType || 'desc',
  })
}

// 分页查询工单派发明细列表 (新接口)
export const getWorkOrderDetailPageSplit = (params: WorkOrderDetailPageDTO) => {
  return request.get<any>('/manage/api/orderWorkDetail/getPageListSplit', {
    current: params.current || 1,
    size: params.size || 10,
    keyword: params.keyword,
    status: params.status,
    orderWordType: params.orderWordType,
    startDate: params.startDate,
    endDate: params.endDate,
    sortColumn: params.sortColumn || 'create_time',
    sortType: params.sortType || 'desc',
  })
}

// 分页查询工单变更明细列表 (新接口)
export const getWorkOrderDetailPageChange = (params: WorkOrderDetailPageDTO) => {
  return request.get<any>('/manage/api/orderWorkDetail/pageChange', {
    current: params.current || 1,
    size: params.size || 10,
    keyword: params.keyword,
    status: params.status,
    orderWordType: params.orderWordType,
    startDate: params.startDate,
    endDate: params.endDate,
    sortColumn: params.sortColumn || 'create_time',
    sortType: params.sortType || 'desc',
  })
}

// 根据工序库Id获取该工艺库的工时统计数据
export const getDetailList = (params: {
  processLibraryId: string | number
  orderId?: string | number
}) => {
  return request.get<any>('/manage/api/orderWorkDetail/getDetailList', params)
}

// 工单报工明细单次信息VO
export interface ReportHistoryVO {
  id: string
  workOrderDetailId: string
  orderId: string
  workOrderNo: string
  processLibraryId: string
  producedQuantity: number
  qualifiedQuantity: number
  unqualifiedQuantity: number
  reworkQuantity: number
  createBy: string
  creator: string
  createTime: string
}

// 获取工单报工明细单次信息
export const getDetailEveryTimeList = (params: {
  processLibraryId: string | number
  orderId?: string | number
}) => {
  return request.get<ReportHistoryVO[]>(
    '/manage/api/orderWorkDetail/getDetailEveryTimeList',
    params,
  )
}

// 工单派发
export const dispatchWorkOrderDetail = (data: OrderWorkDetailSaveDTO) => {
  return request.post<any>('/manage/api/orderWorkDetail/orderDispatch', data)
}

// 工单派发编辑
export const updateDispatchWorkOrderDetail = (data: OrderWorkDetailChangeDTO) => {
  return request.post<any>('/manage/api/orderWorkDetail/orderDispatchUpdate', data)
}

// 工单变更
export const changeWorkOrderDetail = (data: OrderWorkDetailChangeDTO) => {
  return request.post<any>('/manage/api/orderWorkDetail/orderWorkChange', data)
}

// 工单转线
export const transferWorkOrderLine = (data: { id: string | number; deptId: string | number }) => {
  return request.post<any>('/manage/api/orderWorkDetail/transferLine', data)
}

// 工单上线
export const launchWorkOrderDetail = (id: string | number) => {
  return request.post<any>(`/manage/api/orderWorkDetail/launch/${id}`)
}

// 工单下线
export const offlineWorkOrderDetail = (id: string | number) => {
  return request.post<any>(`/manage/api/orderWorkDetail/offline/${id}`)
}

// 工单报工
export const reportWorkOrder = (data: OrderWorkReportDTO) => {
  return request.post<any>('/manage/api/orderWorkDetail/orderReport', data)
}

// 工单变更详情比对信息
export const getWorkOrderChangeDetailInfo = (id: string | number) => {
  return request.get<any>('/manage/api/orderWorkDetail/orderWorkChangeDetailInfo', { id })
}

// 根据工序库Id获取该工艺库的工时统计数据 (汇总)
// export const getDetailList = (processLibraryId: string | number) => {
//   return request.get<any>('/manage/api/orderWorkDetail/getDetailList', { processLibraryId })
// }

// 获取工单报工明细单次信息 (详情)
//   return request.get<any>('/manage/api/orderWorkDetail/getDetailList', { processLibraryId })
// }

// 获取工单报工明细单次信息 (详情)
// export const getDetailEveryTimeList = (processLibraryId: string | number) => {
//   return request.get<any>('/manage/api/orderWorkDetail/getDetailEveryTimeList', {
//     processLibraryId,
//   })
// }

/**
 * 工艺库表单参数信息输入值信息表新增DTO类
 */
export interface ProcessLibraryItemValueSaveDTO {
  id?: string | number
  sorterIndex?: number // 表单添加的次数，用于后续的单次表单数据的聚合
  orderId?: string | number // 任务表id
  processRouteId?: string | number // 工艺路线表id
  processLibraryId?: string | number // 工艺库id
  processLibraryItemId?: string | number // 工艺库表单信息参数输入项主表id
  processLibraryItemParamId?: string | number // 工艺库表单信息参数输入项明细表id
  processLibraryItemParamValue?: string // 工艺库表单信息参数输入值
  viewIndex?: number // 前端页面排版使用
  createBy?: string | number
  createTime?: string
  isDeleted?: number
}

// ==========================================
// 工艺流程详细信息 (New)
// ==========================================

export interface GetAllDetailInfoDTO {
  orderId: string | number
  schedulingId: string | number
  processRouteId: string | number
  detailType?: number
}

export interface ProcessLibraryFileInfoVO {
  id: string
  originalFileName: string
  processLibraryId?: string
  processLibraryItemId?: string
  processLibraryFileType?: number
  fileId?: string
  version: string
  dataMark?: string
  suffixName: string
  fileName: string
  bucketName: string
  createBy?: string
  createTime?: string
}

export interface OrderInfoVO {
  id: string
  orderNo: string
  orderName: string
  processRouteId?: string
  productQuantity: string
  version: string
  orderModel: string
  customerId?: string
  progressStatus?: string
  deliveryTime: string
  contractNo: string
  taskType?: number
  remarks?: string
  createBy?: string
  creator?: string
  createTime?: string
}

export interface ProcessRouteLibraryFlowVO {
  id: string
  processRouteId: string
  processLibraryId: string
  processLibraryName: string
  processIndex: number
  createTime?: string
}

export interface OrderSchedulingVO {
  id: string
  schedulingName: string
  schedulingStartTime: string
  schedulingEndTime: string
  reviewStatus: number
  remarks?: string
}

export interface AllDetailInfoVO {
  orderInfoAllVO: {
    orderInfoVO: OrderInfoVO
    fileAssetsMainVOList: ProcessLibraryFileInfoVO[]
  }
  processRouteDetailVO: {
    processRouteVO: any
    processRouteLibraryFlowList: ProcessRouteLibraryFlowVO[]
    processLibraryFileInfoDOSList: ProcessLibraryFileInfoVO[][]
    processLibraryItemFileInfoDOSList: ProcessLibraryFileInfoVO[][]
    processRouteLibraryDeptMiddleVOList: any[]
  }
  orderWorkDetailAllVO: any
  orderSchedulingVO: OrderSchedulingVO
}

// 获取不合格品登记相关任务和工单数据
export const getOrderAndWorkDetailInfo = (params: {
  orderWorkDetailId: string | number
  orderId: string | number
}) => {
  return request.get<any>('/manage/api/orderWorkDetail/getOrderAndWorkDetailInfo', params)
}

/**
 * 获取详情信息-生产执行时使用
 */
export const getAllDetailInfo = (data: GetAllDetailInfoDTO) => {
  return request.post<AllDetailInfoVO>('/manage/api/getDetailInfo/getAllDetailInfo', data)
}

/**
 * 批量保存工艺库表单输入值
 */
export const saveProcessLibraryItemValues = (data: ProcessLibraryItemValueSaveDTO[]) => {
  return request.post<any>('/manage/api/processLibraryItemParam/saveParamValue', data)
}

// ==========================================
// 工艺执行表单接口 (New)
// ==========================================

export interface ProcessLibraryTableInfoDTO {
  processLibraryId: string | number
  orderId: string | number
  sorterIndex: number
}

export interface ProcessLibraryTableInfoVO {
  sorterIndex: number // 表单顺序
  processLibraryItemId: string // 子表单id
  productName: string // 产品名称 (作为表单名展示)
  completed: string // 是否已填报
}

export interface ProcessLibraryItemDetailDTO {
  processLibraryItemId: string | number
  orderId: string | number
  sorterIndex: number
}

// 工序库信息表VO类
export interface ProcessLibraryVO {
  id: string
  processName: string
  processCode: string
  isKey: number
  processStatus: number
  approvalFlowId?: string
  approvalStatus?: number
  [key: string]: any
}

// 工艺库表单参数信息输入项明细表VO类
export interface ProcessLibraryItemParamVO {
  id: string
  itemParamValueId?: string | number // 填报值记录ID
  processLibraryItemId: string
  paramName: string // 优先使用 paramName (API返回)
  paramType: string | number
  processLibraryItemParamName?: string // 兼容性
  processLibraryItemParamType?: string | number // 兼容性
  jsonConfig?: string
  processLibraryItemParamValue?: string
  paramValue?: string
  viewIndex?: number
  createTime?: string
  [key: string]: any
}

// 工艺库表信息及其工序库对应子表信息VO类
export interface ProcessLibraryItemInfoForWorkParamVO {
  processLibraryVO: ProcessLibraryVO
  id: string // 工艺库表单ID
  complex: number // 1:单数 2:复数
  processLibraryItemId: string
  jsonConfig?: string // 页面格式配置
  processLibraryItemName: string
  remarks?: string
  processLibraryItemParamVOList: ProcessLibraryItemParamVO[]
  [key: string]: any
}

// 获取工单当前工序的表单列表
export const getProcessLibraryItemTableInfo = (params: ProcessLibraryTableInfoDTO) => {
  return request.get<ProcessLibraryTableInfoVO[]>(
    '/manage/api/processLibrary/getProcessLibraryItemTableInfo',
    params,
  )
}

// 获取特定表单的填报详情 (含参数定义和已填值) - 使用正确的接口路径
export const getProcessLibraryItemDetailByOrder = (params: ProcessLibraryItemDetailDTO) => {
  return request.get<ProcessLibraryItemInfoForWorkParamVO>(
    '/manage/api/processLibrary/getProcessLibraryItemInfoForWorkParam',
    params,
  )
}
