import request from '@/utils/request'
import type { WorkOrderDetailVO } from './workOrderDetail'

// 监控页面分页查询DTO
export interface MonitorPageDTO {
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
  deptId?: string
}

// 通用分页请求参数
interface PageParams {
  current: number
  size: number
}

// 待执行工单列表 (待执行队列)
export const getNoExecutePageList = (
  params: MonitorPageDTO,
  page: PageParams = { current: 1, size: 1000 },
) => {
  return request.get<any>('/manage/api/orderWorkDetailReview/getNoExecutePageList', {
    ...page,
    ...params,
  })
}

// 执行中工单列表 (执行中)
export const getWaitExecutePageList = (
  params: MonitorPageDTO,
  page: PageParams = { current: 1, size: 1000 },
) => {
  return request.get<any>('/manage/api/orderWorkDetailReview/getWaitExecutePageList', {
    ...page,
    ...params,
  })
}

// 已完成工单列表 (今日完工)
export const getAlreadyExecutePageList = (
  params: MonitorPageDTO,
  page: PageParams = { current: 1, size: 1000 },
) => {
  return request.get<any>('/manage/api/orderWorkDetailReview/getAlreadyExecutePageList', {
    ...page,
    ...params,
  })
}

// 产能分析 - 已完成执行工单列表 (不分页)
export const getAlreadyExecuteWorkDetailList = (params: MonitorPageDTO) => {
  return request.get<any>('/manage/api/orderWorkDetailReview/getAlreadyExecuteWorkDetailList', {
    ...params,
  })
}
