export interface SysRole {
  roleId: string
  roleName: string
  roleCode: string
  roleDesc: string
  createTime?: string
  updateTime?: string
  createBy?: string
  updateBy?: string
  delFlag?: string
}

export interface RoleVo {
  roleId: string
  menuIds: string
}

export interface RolePageQuery {
  current?: number
  size?: number
  roleName?: string
}
