import request from '../utils/request'
import type { 
  SysDept, 
  DeptTreeNode, 
  DeptSaveRequest, 
  UpdateUserDeptRequest,
  DeptQueryParams,
  DeptPageParams 
} from '../types/dept'

// API响应结构
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

// 分页响应
interface PageResponse<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

/**
 * 获取部门树形菜单（统一使用 tree 接口）
 */
export const getDeptTreeApi = (userId?: number, isAdmin?: number): Promise<ApiResponse<any[]>> => {
  const params: Record<string, any> = {}
  if (userId !== undefined) params.userId = userId
  if (isAdmin !== undefined) params.isAdmin = isAdmin
  
  return request.get('/admin/dept/tree', params)
}

/**
 * 获取当前用户的部门树
 */
export const getUserDeptTreeApi = (isAdmin?: boolean): Promise<ApiResponse<any[]>> => {
  const params: Record<string, any> = {}
  if (isAdmin !== undefined) params.isAdmin = isAdmin
  
  return request.get('/admin/dept/user-tree', params)
}

/**
 * 分页查询部门
 */
export const getDeptPageApi = (pageParams: DeptPageParams, queryParams?: DeptQueryParams): Promise<ApiResponse<PageResponse<SysDept>>> => {
  const params = {
    page: {
      current: pageParams.current,
      size: pageParams.size,
    },
    dto: {
      sortColumn: 'sort_order',
      sortType: 'asc',
      ...queryParams,
    },
  }
  
  return request.get('/admin/dept/page', params)
}

/**
 * 通过ID查询部门详情
 */
export const getDeptByIdApi = (id: string): Promise<ApiResponse<SysDept>> => {
  return request.get(`/admin/dept/${id}`)
}

/**
 * 根据部门名称查询部门信息
 */
export const getDeptByNameApi = (deptName: string): Promise<ApiResponse<SysDept>> => {
  return request.get(`/admin/dept/details/${encodeURIComponent(deptName)}`)
}

/**
 * 添加部门
 */
export const addDeptApi = (deptData: Partial<SysDept>, userIdList?: string[]): Promise<ApiResponse<any>> => {
  const requestBody: DeptSaveRequest = {
    sysDept: deptData,
    userIdList: userIdList || [],
  }
  
  return request.post('/admin/dept', requestBody)
}

/**
 * 编辑部门
 */
export const updateDeptApi = (deptData: Partial<SysDept>, userIdList?: string[]): Promise<ApiResponse<any>> => {
  const requestBody: DeptSaveRequest = {
    sysDept: deptData,
    userIdList: userIdList || [],
  }
  
  return request.put('/admin/dept', requestBody)
}

/**
 * 删除部门
 */
export const deleteDeptApi = (id: string): Promise<ApiResponse<any>> => {
  return request.delete(`/admin/dept/${id}`)
}

/**
 * 启用/停用部门
 */
export const toggleDeptEnabledApi = (id: string, type: 0 | 1): Promise<ApiResponse<any>> => {
  return request.get('/admin/dept/enabled', { id, type })
}

/**
 * 更新部门用户
 */
export const updateDeptUsersApi = (deptId: string, userIdList: string[]): Promise<ApiResponse<any>> => {
  const requestBody: UpdateUserDeptRequest = {
    deptId,
    userIdList,
  }
  
  return request.post('/admin/dept/updateUserDeptId', requestBody)
}
