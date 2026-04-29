import request from '@/utils/request'

export interface CodeRuleVO {
  id: string
  type: number
  prefix: string
  ruleName: string
  isEnable: number
  remark: string
  createBy: string
  createTime: string
  updateBy: string
  updateTime: string
}

export interface CodeRulePageDTO {
  id?: string
  type?: number
  keyword?: string
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: string
  current?: number
  size?: number
}

export interface CodeRuleUpdateDTO {
  id?: string
  type: number
  prefix: string
  ruleName: string
  remark?: string
  isEnable: number
}

interface CodeRulePageResult {
  records: CodeRuleVO[]
  total: number
  size: number
  current: number
  pages: number
}

// 分页查询编码规则配置
export const getCodeRulePage = (params: CodeRulePageDTO) => {
  return request.get<CodeRulePageResult>('/manage/api/codeRule/page', {
    current: params.current || 1,
    size: params.size || 10,
    ...params,
  })
}

// 通过id查询编码规则详情
export const getCodeRuleDetail = (id: string) => {
  return request.get<CodeRuleVO>(`/manage/api/codeRule/${id}`)
}

// 编辑编码规则
export const updateCodeRule = (data: CodeRuleUpdateDTO) => {
  return request.post<boolean>('/manage/api/codeRule/update', data)
}

// 新增编码规则
export const saveCodeRule = (data: CodeRuleUpdateDTO) => {
  return request.post<boolean>('/manage/api/codeRule/save', data)
}

// 启用/禁用编码规则
export const enableCodeRule = (id: string, isEnable: number) => {
  return request.post<boolean>('/manage/api/codeRule/enableCodeRule', null, {
    params: { id, isEnable },
  })
}

// 根据编码规则类型获取编码
export const getCode = (codeType: number) => {
  return request.post<string>('/manage/api/codeRule/getCode', null, {
    params: { codeType },
  })
}
