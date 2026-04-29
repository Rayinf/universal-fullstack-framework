// 用户管理相关类型定义

export interface Role {
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  roleId: string
  roleName: string
  roleCode?: string
  roleDesc?: string
  delFlag?: string
}

export interface Post {
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  postId: number
  postCode?: string
  postName: string
  postSort?: number
  delFlag?: string
  remark?: string
}

export interface UserRecord {
  userId: string
  username: string
  password?: string
  salt?: string
  createTime?: string
  updateTime?: string
  delFlag?: string
  lockFlag?: string
  phone?: string
  email?: string
  avatar?: string
  deptId?: number
  deptName?: string
  examiner?: number
  examinerName?: string
  examineStatus?: number
  examineContent?: string
  examineTime?: string
  enabled?: number
  realName?: string
  createBy?: number
  creator?: string
  roleList?: Role[]
  postList?: Post[]
  isAdmin?: boolean
  roleId?: string
  spaceSize?: number
  spaceSizeStr?: string
  lastLoginTime?: string
  tenantCode?: string
  tenantName?: string
}

export interface UserCreateDto {
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  userId?: string
  username: string
  password: string
  lockFlag?: string
  phone?: string
  email?: string
  avatar?: string
  deptId?: number
  delFlag?: string
  examiner?: number
  examineStatus?: number
  examineContent?: string
  examineTime?: string
  enabled?: number
  realName: string
  spaceSize?: number
  tenantCode?: string
  role?: string | string[] // 支持单个角色ID或角色ID数组
  post?: number[]
  password1?: string
  newpassword1?: string
}

export interface UserUpdateDto {
  userId: string
  deptId?: number
  realName?: string
  phone?: string
  email?: string
  password?: string
  oldPassword?: string
  password1?: string
  spaceSize?: number
  role?: string | string[] // 支持单个角色ID或角色ID数组
}

export interface UserPageQuery {
  sortColumn?: string
  sortType?: 'asc' | 'desc'
  username?: string
  realName?: string
  deptId?: number
  role?: string
  roleId?: string
  enabled?: number
  examineStatus?: number
  startTime?: string
  endTime?: string
  deptIdList?: number[]
  tenantCode?: string
}

export interface UserPageRequest {
  records?: unknown[]
  total?: number
  size: number
  current: number
  optimizeJoinOfCountSql?: boolean
  pages?: number
}

export interface UserIPage<T> {
  size: number
  total: number
  pages: number
  current: number
  records: T[]
}

export interface UserApiResponse<T> {
  code: number
  msg: string | null
  data?: T // data字段可选，因为后端可能不返回data
}
