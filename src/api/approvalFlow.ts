import request from '@/utils/request'
import type {
  ApprovalFlow,
  ApprovalFlowDetail,
  ApprovalFlowNodeSaveDTO,
  ApprovalFlowPageQuery,
  ApprovalFlowSaveDTO,
  ApprovalFlowUpdateDTO,
  ApprovalFlowResultQuery,
  ApprovalFlowResultVO,
  IPage,
  PageRequest,
  ApiResponse,
} from '@/types/approvalFlow'

interface ApprovalFlowResultPageQuery extends ApprovalFlowResultQuery, PageRequest {}

interface ApprovalResultListQuery extends ApprovalFlowResultQuery {
  current?: number
  size?: number
}

/**
 * 分页查询审批规则信息
 */
export const pageApprovalFlowApi = (params: ApprovalFlowPageQuery & PageRequest) => {
  return request.get<ApiResponse<IPage<ApprovalFlow>>>('/manage/api/approvalFlow/page', params)
}

/**
 * 查询审批规则信息list列表
 */
export const listApprovalFlowApi = () => {
  return request.get<ApiResponse<ApprovalFlow[]>>('/manage/api/approvalFlow/list')
}

/**
 * 根据审批规则id查询详情信息（包含节点信息）
 */
export const getApprovalFlowDetailApi = (approvalFlowId: number) => {
  return request.get<ApiResponse<ApprovalFlowDetail[]>>(
    '/manage/api/approvalFlow/detailByApprovalFlowId',
    { approvalFlowId },
  )
}

/**
 * 添加审批规则信息
 */
export const saveApprovalFlowApi = (data: ApprovalFlowSaveDTO) => {
  return request.post<ApiResponse<unknown>>('/manage/api/approvalFlow/save', data)
}

/**
 * 编辑审批规则信息
 */
export const updateApprovalFlowApi = (data: ApprovalFlowUpdateDTO) => {
  return request.post<ApiResponse<unknown>>('/manage/api/approvalFlow/update', data)
}

/**
 * 删除审批规则信息
 */
export const deleteApprovalFlowApi = (id: number) => {
  return request.delete<ApiResponse<unknown>>(`/manage/api/approvalFlow/${id}`)
}

/**
 * 添加审批规则的审核节点信息
 */
export const saveApprovalFlowNodesApi = (data: ApprovalFlowNodeSaveDTO[]) => {
  return request.post<ApiResponse<unknown>>(
    '/manage/api/approvalFlow/saveApprovalFlowNodeInfo',
    data,
  )
}

/**
 * 分页查询审批结果信息
 */
export const pageApprovalFlowResultApi = (params: ApprovalFlowResultPageQuery) => {
  return request.get<IPage<ApprovalFlowResultVO>>('/manage/api/approvalFlowResult/page', params)
}

/**
 * 获取审批结果列表 (通知用)
 */
export const getApprovalResultListApi = (data: ApprovalResultListQuery) => {
  return request.post<ApprovalFlowResultVO[]>('/manage/api/approvalFlowResult/getApprovalResultList', data)
}
