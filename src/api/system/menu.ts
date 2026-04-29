import request from '@/utils/request'
import type { MenuNode, MenuQuery } from '@/types/system/menu'

// 获取菜单树
export const getMenuTreeApi = (params?: MenuQuery) => {
  return request.get<MenuNode[]>('/admin/menu/tree', params)
}

// 获取角色的菜单ID列表
export const getRoleMenuIdsApi = (roleId: string | number) => {
  return request.get<string[]>(`/admin/menu/tree/${roleId}`)
}
