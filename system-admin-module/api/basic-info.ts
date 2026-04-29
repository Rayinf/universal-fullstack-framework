import { request } from '@/api/http'
import type { 
  BasicInfoApiResponse, 
  BasicInfoDto, 
  BasicInfoPageQuery, 
  BasicInfoRecord, 
  BasicInfoIPage, 
  BasicInfoPageRequest 
} from '@/types/basic-info'

// 分页查询基础信息维护
export const pageBasicInfoApi = (params: BasicInfoPageQuery & BasicInfoPageRequest) =>
  request<BasicInfoApiResponse<BasicInfoIPage<BasicInfoRecord>>>({
    url: '/manage/api/basicInformation/page',
    method: 'get',
    params,
  })

// 根据类型获取分类列表
export const listBasicInfoByTypeApi = (type: number) =>
  request<BasicInfoApiResponse<BasicInfoRecord[]>>({
    url: '/manage/api/basicInformation/list',
    method: 'get',
    params: { type },
  })

// 新增分类
export const saveBasicInfoApi = (data: BasicInfoDto) => {
  const requestData: any = {
    name: data.name,
    type: data.type
  }
  
  // 如果有 parentId，则添加到请求数据中
  if (data.parentId !== undefined && data.parentId !== null) {
    requestData.parentId = data.parentId
  }
  
  return request<BasicInfoApiResponse<unknown>>({
    url: '/manage/api/basicInformation/save',
    method: 'post',
    data: requestData,
  })
}

// 修改分类
export const updateBasicInfoApi = (data: BasicInfoDto) => {
  const requestData: any = {
    id: data.id,
    name: data.name,
    type: data.type
  }
  
  // 如果有 parentId，则添加到请求数据中
  if (data.parentId !== undefined && data.parentId !== null) {
    requestData.parentId = data.parentId
  }
  
  return request<BasicInfoApiResponse<unknown>>({
    url: '/manage/api/basicInformation/update',
    method: 'post',
    data: requestData,
  })
}

// 根据id删除分类
export const deleteBasicInfoApi = (id: number) =>
  request<BasicInfoApiResponse<unknown>>({
    url: `/manage/api/basicInformation/${id}`,
    method: 'delete',
  })
