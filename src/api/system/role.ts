import request from '@/utils/request'
import type { SysRole, RoleVo, RolePageQuery } from '@/types/system/role'

interface RolePageData {
  records: SysRole[]
  total: number
  size: number
  current: number
  pages: number
}

// 获取角色分页
export const getRolePageApi = (params: RolePageQuery) => {
  return request.get<RolePageData>('/admin/role/page', params)
}

// 获取角色列表
export const getRoleListApi = () => {
  return request.get<SysRole[]>('/admin/role/list')
}

// 根据ID获取角色
export const getRoleByIdApi = (id: string | number) => {
  return request.get<SysRole>(`/admin/role/${id}`)
}

// 添加角色
export const addRoleApi = (data: Partial<SysRole>) => {
  return request.post<boolean>('/admin/role', data)
}

// 修改角色
export const updateRoleApi = (data: Partial<SysRole>) => {
  return request.put<boolean>('/admin/role', data)
}

// 删除角色
export const deleteRoleApi = (id: string | number) => {
  return request.delete<boolean>(`/admin/role/${id}`)
}

// 更新角色菜单权限
export const updateRoleMenusApi = (data: RoleVo) => {
  return request.put<boolean>('/admin/role/menu', data)
}

// 获取角色下的用户ID列表
export const getUsersByRoleIdApi = (roleId: string | number) => {
  return request.get<number[]>('/admin/role/getUserByRoleId', { roleId })
}

// 导出角色
export const exportRoleApi = () => {
  return request.get<unknown[]>('/admin/role/export', { responseType: 'blob' })
}
