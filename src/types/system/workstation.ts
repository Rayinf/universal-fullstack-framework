export interface WorkstationRecord {
  id: string
  workstationNo: number // 工位编号
  workstationName: string // 工位名称
  workstationType: number // 工位类型 (1:装配 2:测试 3:包装, 4:维修)
  status: number // 状态: 1-启用, 0-禁用
  responsiblePerson: string // 负责人
  responsiblePersonName?: string // 负责人名称
  deptId: string // 所属产线ID (部门ID)
  deptName?: string // 所属产线名称 (部门名称)
  processLibraryId: string // 关联工序ID
  processLibraryName?: string // 关联工序名称
  createTime?: string
  updateTime?: string
  remarks?: string
}

export interface WorkstationQuery {
  workstationName?: string
  workstationType?: number
  status?: number
  deptId?: string // 部门ID查询
  keywords?: string
  current?: number
  page?: number
  size?: number
  sortColumn?: string
  sortType?: string
}

export interface WorkstationDTO {
  id?: string
  workstationNo: number
  workstationName: string
  workstationType: number
  status: number
  responsiblePerson?: string
  deptId?: string
  processLibraryId?: string
  remarks?: string
}

export interface WorkstationIPage {
  records: WorkstationRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface WorkstationApiResponse<T> {
  code: number
  msg: string
  data?: T
}
