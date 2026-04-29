export interface BasicCrudRecord {
  id: string
  name: string
  code: string
  remark?: string
  status: number
  createTime: string
  updateTime: string
}

export interface BasicCrudPageParams {
  current: number
  size: number
  keyword?: string
}

export interface BasicCrudPageData {
  records: BasicCrudRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface BasicCrudSaveDto {
  name: string
  code: string
  remark?: string
  status: number
}
