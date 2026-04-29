import request from '@/utils/request'
import type {
  NonConformingReport,
  NonConformingQueryDTO,
  NonConformingDetailRes,
} from '@/types/quality/nonConforming'

enum Api {
  Page = '/manage/api/unqualifiedProductReport/page',
  Detail = '/manage/api/unqualifiedProductReport/', // + id
  Save = '/manage/api/unqualifiedProductReport/saveReport',
  Update = '/manage/api/unqualifiedProductReport/updateReport',
  Void = '/manage/api/unqualifiedProductReport/void/', // + id
}

// 分页查询不合格品登记信息
export const getNonConformingPage = (params: NonConformingQueryDTO) => {
  return request.get(Api.Page, {
    ...params.page,
    ...params.dto,
    sortColumn: 'create_time',
    sortType: 'desc',
  })
}

// 通过ID查询不合格品登记信息详情
export const getNonConformingDetail = (id: string) => {
  return request.get<NonConformingDetailRes>(`${Api.Detail}${id}`)
}

// 添加不合格品登记信息
export const createNonConformingReport = (data: Partial<NonConformingReport>) => {
  return request.post(Api.Save, data)
}

// 编辑不合格品登记信息 (包含责任部门的原因分析)
export const updateNonConformingReport = (data: Partial<NonConformingReport>) => {
  return request.post(Api.Update, data)
}

// 不合格品登记表作废
export const voidNonConformingReport = (id: string) => {
  return request.post(`${Api.Void}${id}`)
}
