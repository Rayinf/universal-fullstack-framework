// 生产工单相关API服务
import request from '@/utils/request'
import type {
  WorkOrder,
  WorkOrderChange,
  WorkOrderRelation,
  ProcessReport,
  WorkOrderHistory,
  ProductionPlan,
  ProcessRoute,
  ProductionResource,
  ResourceAvailableTime,
  GenerateWorkOrderRequest,
  DispatchWorkOrderRequest,
  ChangeWorkOrderRequest,
  OnlineConfirmRequest,
  OfflineConfirmRequest,
  ApiResponse,
  PageResponse,
  ValidationResult,
} from '@/types/workOrder'

// 工单管理API
export const workOrderApi = {
  // 获取工单列表
  getWorkOrders(params: {
    status?: string
    processName?: string
    productModel?: string
    productionLine?: string
    page?: number
    pageSize?: number
  }) {
    return request.get<PageResponse<WorkOrder>>('/production/workorder/list', {
      params,
    })
  },

  // 获取工单详情
  getWorkOrderDetail(id: string) {
    return request.get<WorkOrder>(`/production/workorder/detail/${id}`)
  },

  // 生成工单
  generateWorkOrders(data: GenerateWorkOrderRequest) {
    return request.post<{ planCode: string; generatedCount: number; workOrders: WorkOrder[] }>(
      '/production/workorder/generate',
      data,
    )
  },

  // 批量生成工单
  batchGenerateWorkOrders(planIds: string[]) {
    return request.post<{ success: boolean; generatedCount: number; errors: string[] }>(
      '/production/workorder/batch-generate',
      { planIds },
    )
  },

  // 校验工单生成
  validateGenerate(planIds: string[]) {
    return request.post<ValidationResult>('/production/workorder/validate-generate', {
      planIds,
    })
  },

  // 派发工单
  dispatchWorkOrder(data: DispatchWorkOrderRequest) {
    return request.post<void>('/production/workorder/dispatch', data)
  },

  // 批量派发工单
  batchDispatchWorkOrders(data: DispatchWorkOrderRequest) {
    return request.post<void>('/production/workorder/batch-dispatch', data)
  },

  // 校验派发
  validateDispatch(data: DispatchWorkOrderRequest) {
    return request.post<ValidationResult>('/production/workorder/validate-dispatch', data)
  },

  // 获取资源可用时间
  getResourceAvailableTime(resourceId: string, startDate: string, endDate: string) {
    return request.get<ResourceAvailableTime[]>('/production/resource/available-time', {
      params: { resourceId, startDate, endDate },
    })
  },

  // 合并工单
  mergeWorkOrders(data: ChangeWorkOrderRequest) {
    return request.post<{ newWorkOrderId: string; newWorkOrderCode: string }>(
      '/production/workorder/merge',
      data,
    )
  },

  // 拆分工单
  splitWorkOrder(data: ChangeWorkOrderRequest) {
    return request.post<{ newWorkOrderIds: string[]; newWorkOrderCodes: string[] }>(
      '/production/workorder/split',
      data,
    )
  },

  // 转线工单
  transferWorkOrder(data: ChangeWorkOrderRequest) {
    return request.post<void>('/production/workorder/transfer', data)
  },

  // 获取工单变更历史
  getWorkOrderChanges(workOrderId: string) {
    return request.get<WorkOrderChange[]>(`/production/workorder/changes/${workOrderId}`)
  },

  // 获取工单关联关系
  getWorkOrderRelations(workOrderId: string) {
    return request.get<WorkOrderRelation[]>(`/production/workorder/relations/${workOrderId}`)
  },

  // 上线确认
  confirmOnline(data: OnlineConfirmRequest) {
    return request.post<void>('/production/workorder/online-confirm', data)
  },

  // 下线确认
  confirmOffline(data: OfflineConfirmRequest) {
    return request.post<void>('/production/workorder/offline-confirm', data)
  },

  // 获取工单操作历史
  getWorkOrderHistory(workOrderId: string) {
    return request.get<WorkOrderHistory[]>(`/production/workorder/history/${workOrderId}`)
  },

  // 取消工单
  cancelWorkOrder(workOrderId: string, reason: string) {
    return request.post<void>(`/production/workorder/cancel/${workOrderId}`, {
      reason,
    })
  },

  // 暂停工单
  pauseWorkOrder(workOrderId: string, reason: string) {
    return request.post<void>(`/production/workorder/pause/${workOrderId}`, { reason })
  },

  // 恢复工单
  resumeWorkOrder(workOrderId: string) {
    return request.post<void>(`/production/workorder/resume/${workOrderId}`)
  },
}

// 生产计划API（用于工单生成）
export const productionPlanApi = {
  // 获取待生成工单的计划列表
  getPlansForGenerate(params: {
    status?: string
    productModel?: string
    productionLine?: string
    page?: number
    pageSize?: number
  }) {
    return request.get<PageResponse<ProductionPlan>>('/production/plan/list-for-generate', {
      params,
    })
  },

  // 获取计划详情
  getPlanDetail(id: string) {
    return request.get<ProductionPlan>(`/production/plan/detail/${id}`)
  },

  // 校验计划是否可生成工单
  validatePlanForGenerate(planId: string) {
    return request.get<ValidationResult>(`/production/plan/validate/${planId}`)
  },
}

// 工艺路线API
export const processRouteApi = {
  // 获取产品的工艺路线
  getProcessRouteByProduct(productId: string) {
    return request.get<ProcessRoute>(`/technology/process-route/by-product/${productId}`)
  },

  // 获取工艺路线详情
  getProcessRouteDetail(id: string) {
    return request.get<ProcessRoute>(`/technology/process-route/detail/${id}`)
  },
}

// 生产资源API
export const productionResourceApi = {
  // 获取资源列表
  getResources(params: {
    resourceType?: 'productionLine' | 'workTeam' | 'workstation'
    status?: string
    parentId?: string
    page?: number
    pageSize?: number
  }) {
    return request.get<PageResponse<ProductionResource>>('/production/resource/list', {
      params,
    })
  },

  // 获取资源详情
  getResourceDetail(id: string) {
    return request.get<ProductionResource>(`/production/resource/detail/${id}`)
  },
}

// 工序报工API
export const processReportApi = {
  // 获取报工记录列表
  getReports(params: {
    workOrderId?: string
    processCode?: string
    operatorId?: string
    startDate?: string
    endDate?: string
    page?: number
    pageSize?: number
  }) {
    return request.get<PageResponse<ProcessReport>>('/production/report/list', {
      params,
    })
  },

  // 提交报工
  submitReport(data: Partial<ProcessReport> & { workOrderId: string }) {
    return request.post<ProcessReport>('/production/report/submit', data)
  },

  // 修改报工
  updateReport(reportId: string, data: Partial<ProcessReport>) {
    return request.put<void>(`/production/report/${reportId}`, data)
  },

  // 获取工单报工汇总
  getReportSummary(workOrderId: string) {
    return request.get<{
      totalReport: number
      totalQualified: number
      totalUnqualified: number
      totalRework: number
      reports: ProcessReport[]
    }>(`/production/report/summary/${workOrderId}`)
  },
}

export default {
  workOrder: workOrderApi,
  plan: productionPlanApi,
  processRoute: processRouteApi,
  resource: productionResourceApi,
  report: processReportApi,
}
