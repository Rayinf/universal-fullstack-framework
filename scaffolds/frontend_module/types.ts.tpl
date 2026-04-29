// 初始骨架默认使用 name/code/status/remark 字段，生成后请按业务字段调整。

export interface __MODULE_PASCAL__Record {
  id: string
  name: string
  code: string
  remark?: string
  status: number
  createTime: string
  updateTime: string
}

export interface __MODULE_PASCAL__PageParams {
  current: number
  size: number
  keyword?: string
}

export interface __MODULE_PASCAL__PageData {
  records: __MODULE_PASCAL__Record[]
  total: number
  size: number
  current: number
  pages: number
}

export interface __MODULE_PASCAL__SaveDto {
  name: string
  code: string
  remark?: string
  status: number
}
