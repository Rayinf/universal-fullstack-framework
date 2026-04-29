import request from '@/utils/request'

// 工单分页查询DTO
export interface WorkOrderPageDTO {
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

// 工单信息VO
export interface WorkOrderVO {
  id: string // 主键id
  workOrderNo: string // 工单号
  workQuantity: number // 该工序需产品数量
  orderId: string // 任务表id
  orderName: string // 任务名称
  processRouteId: string // 工艺路线表id
  processRouteName: string // 工艺路线名称
  orderSchedulingId: string // 工单排程id
  orderSchedulingName: string // 工单排程名称
  status: number // 工单状态 1：待派发 2：已派发 3:执行中 4：已完成
  createBy: string // 创建人
  creator: string // 创建人名称
  createTime: string // 创建时间
  isDeleted: number // 是否删除
}

// 分页查询工单列表信息
export const getWorkOrderPage = (params: WorkOrderPageDTO) => {
  return request.get<any>('/manage/api/orderWork/page', {
    current: params.current || 1,
    size: params.size || 10,
    keyword: params.keyword,
    status: params.status,
    orderWordType: params.orderWordType,
    startDate: params.startDate,
    endDate: params.endDate,
    sortColumn: params.sortColumn || 'create_time', // 默认按创建时间排序
    sortType: params.sortType || 'desc', // 默认降序
  })
}

// 工单手动拆分
export const splitWorkOrder = (id: string | number) => {
  return request.get<any>('/manage/api/orderWork/orderSplit', { id })
}
