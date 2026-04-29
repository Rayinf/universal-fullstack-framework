export interface DeviceRecord {
  id: string
  deviceName: string // 设备名称
  deviceNumber: string // 设备编号
  model: string // 设备型号
  deviceCategoryId: string // 资产类型ID
  deviceCategoryName?: string // 资产类型名称
  workstationId: string // 所属工位ID
  workstationName?: string // 所属工位名称
  responsiblePerson: string // 责任人
  responsiblePersonName?: string // 责任人名称
  status: number // 设备状态：1:启用 2:停用 3:报废
  remarks?: string // 设备备注信息
  scrapReason?: string // 报废原因
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  isDeleted?: number
}

export interface DeviceQuery {
  keyWord?: string // 关键词：名称/编号
  deviceCategoryId?: string
  status?: number
  workstationId?: string
  current?: number
  page?: number
  size?: number
  sortColumn?: string
  sortType?: string
}

export interface DeviceDTO {
  id?: string
  deviceName: string
  deviceNumber: string
  model: string
  deviceCategoryId: string
  workstationId: string
  responsiblePerson: string
  status: number
  remarks?: string
  scrapReason?: string
}

export interface DeviceIPage {
  records: DeviceRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface DeviceApiResponse<T> {
  code: number
  msg: string
  data?: T
}

// 设备状态枚举
export enum DeviceStatus {
  ENABLE = 1,
  DISABLE = 2,
  SCRAP = 3,
}

export const DEVICE_STATUS_MAP: Record<number, string> = {
  [DeviceStatus.ENABLE]: '启用',
  [DeviceStatus.DISABLE]: '停用',
  [DeviceStatus.SCRAP]: '报废',
}
