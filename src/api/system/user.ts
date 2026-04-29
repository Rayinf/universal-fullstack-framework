import request from '@/utils/request'
import type {
  UserApiResponse,
  UserCreateDto,
  UserUpdateDto,
  UserPageQuery,
  UserRecord,
  UserIPage,
  UserPageRequest,
} from '@/types/system/user'

// 分页查询用户
export const pageUsersApi = (params: UserPageQuery & UserPageRequest) =>
  request.get<UserIPage<UserRecord>>('/admin/user/page', params)

// 通过ID查询用户信息
export const getUserDetailApi = (id: string) =>
  request.get<UserRecord>(`/admin/user/${id}`)

// 添加用户
export const createUserApi = (data: UserCreateDto) =>
  request.post<unknown>('/admin/user', data)

// 获取所有普通用户
export const getAllUsersApi = () =>
  request.get<UserApiResponse<UserRecord[]>>('/admin/user/getAllUser')

// 管理员更新用户信息
export const updateUserApi = (data: UserUpdateDto) =>
  request.put<UserApiResponse<unknown>>('/admin/user', data)

// 删除用户信息
export const deleteUserApi = (id: string) =>
  request.delete<UserApiResponse<unknown>>(`/admin/user/${id}`)

// 初始化密码
export const resetUserPasswordApi = (id: string) =>
  request.get<UserApiResponse<unknown>>(`/admin/user/resetPwd/${id}`)

// 修改个人密码信息
export const updateUserPasswordApi = (data: UserUpdateDto) =>
  request.put<UserApiResponse<unknown>>('/admin/user/updatePwd', data)

// 修改个人基本信息
export const updateUserBaseInfoApi = (data: UserUpdateDto) =>
  request.post<UserApiResponse<unknown>>('/admin/user/updateBaseInfo', data)

// 启用/禁用用户账号
export const toggleUserEnabledApi = (id: string, enabled: number) =>
  request.get<UserApiResponse<unknown>>('/admin/user/enabled', { id, enabled })
