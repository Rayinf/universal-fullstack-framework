export interface ProjectRecord {
  id: string
  projectCode: string
  projectName: string
  ownerName: string
  priority: number
  status: number
  progress: number
  startDate: string
  endDate: string
  remark: string
  createTime: string
  updateTime: string
}

export interface ProjectPageParams {
  current: number
  size: number
  keyword?: string
  status?: number
}

export interface ProjectPageData {
  records: ProjectRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface ProjectSaveDto {
  projectCode: string
  projectName: string
  ownerName: string
  priority: number
  status: number
  progress: number
  startDate: string
  endDate: string
  remark: string
}
