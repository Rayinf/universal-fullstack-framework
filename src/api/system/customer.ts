import request from '@/utils/request'
import type { Customer, CustomerPageQuery, CustomerPageRequest } from '@/types/system/customer'

const BASE_URL = '/manage/api/customers'

export interface CustomerPageData {
  records: Customer[]
  total: number
  size: number
  current: number
  pages: number
}

// 分页查询客户信息
export function pageCustomersApi(params: CustomerPageQuery & CustomerPageRequest) {
  return request.get<CustomerPageData>(`${BASE_URL}/page`, params)
}

// 查询客户信息列表
export function listCustomersApi() {
  return request.get<Customer[]>(`${BASE_URL}/list`)
}

// 通过ID查询客户详情
export function getCustomerByIdApi(id: string | number) {
  return request.get<Customer>(`${BASE_URL}/${id}`)
}

// 添加客户信息
export function saveCustomerApi(data: Partial<Customer>) {
  return request.post<boolean>(`${BASE_URL}/save`, data)
}

// 编辑客户信息
export function updateCustomerApi(data: Partial<Customer>) {
  return request.post<boolean>(`${BASE_URL}/update`, data)
}

// 删除客户信息
export function deleteCustomerApi(id: string | number) {
  return request.delete<boolean>(`${BASE_URL}/${id}`)
}
