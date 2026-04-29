export interface SystemUser {
  id: string
  username: string
  name: string
  role: string
  roleLabel: string
  status: boolean
  updatedAt: string
  email?: string
  phone?: string
  department?: string
  createdAt?: string
}

export interface SystemUserQuery {
  keyword?: string
  role?: string
}

export interface OperationLog {
  id: string
  operator: string
  module: string
  action: string
  status: 'success' | 'failed'
  ip: string
  createTime: string
  request: string
  response: string
}

export interface OperationLogQuery {
  operator?: string
  module?: string
  range?: Date[]
}

export interface BackupRecord {
  id: string
  name: string
  operator: string
  type: string
  status: 'success' | 'failed'
  createdAt: string
  size?: string
  description?: string
}
