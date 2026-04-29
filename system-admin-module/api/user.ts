import { request } from '@/api/http'
import type { 
  UserApiResponse, 
  UserCreateDto, 
  UserUpdateDto, 
  UserPageQuery, 
  UserRecord, 
  UserIPage, 
  UserPageRequest 
} from '@/types/user'

// 分页查询用户
export const pageUsersApi = (params: UserPageQuery & UserPageRequest) =>
  request<UserApiResponse<UserIPage<UserRecord>>>({
    url: '/admin/user/page',
    method: 'get',
    params,
  })

// 通过ID查询用户信息
export const getUserDetailApi = (id: string | number) =>
  request<UserApiResponse<UserRecord>>({
    url: `/admin/user/${id}`,
    method: 'get',
  })

// 添加用户
export const createUserApi = (data: UserCreateDto) =>
  request<UserApiResponse<unknown>>({
    url: '/admin/user',
    method: 'post',
    data,
  })

// 获取所有普通用户
export const getAllUsersApi = () =>
  request<UserApiResponse<UserRecord[]>>({
    url: '/admin/user/getAllUser',
    method: 'get',
  })

// 管理员更新用户信息
export const updateUserApi = (data: UserUpdateDto) =>
  request<UserApiResponse<unknown>>({
    url: '/admin/user',
    method: 'put',
    data,
  })

// 删除用户信息
export const deleteUserApi = (id: string | number) =>
  request<UserApiResponse<unknown>>({
    url: `/admin/user/${id}`,
    method: 'delete',
  })

// 初始化密码
export const resetUserPasswordApi = (id: string | number) =>
  request<UserApiResponse<unknown>>({
    url: '/admin/user/resetPwd',
    method: 'get',
    params: { id },
  })

// 修改个人密码信息
export const updateUserPasswordApi = (data: UserUpdateDto) =>
  request<UserApiResponse<unknown>>({
    url: '/admin/user/updatePwd',
    method: 'put',
    data,
  })

// 修改个人基本信息
export const updateUserBaseInfoApi = (data: UserUpdateDto) =>
  request<UserApiResponse<unknown>>({
    url: '/admin/user/updateBaseInfo',
    method: 'post',
    data,
  })

// 启用/禁用用户账号
export const toggleUserEnabledApi = (id: string | number, enabled: number) =>
  request<UserApiResponse<unknown>>({
    url: '/admin/user/enabled',
    method: 'get',
    params: { id, enabled },
  })
