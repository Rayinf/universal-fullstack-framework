import request from '@/utils/request'
import type {
  DeviceQuery,
  DeviceRecord,
  DeviceDTO,
  DeviceIPage,
  DeviceApiResponse,
} from '@/types/system/device'

// 分页查询设备信息
export const pageDevicesApi = (params: DeviceQuery) =>
  request.get<DeviceIPage>('/manage/api/deviceInfo/page', params)

// 获取所有设备信息
export const getDeviceListApi = () =>
  request.get<DeviceApiResponse<DeviceRecord[]>>('/manage/api/deviceInfo/list')

// 通过ID查询设备详情信息
export const getDeviceDetailApi = (id: string) =>
  request.get<DeviceApiResponse<DeviceRecord>>(`/manage/api/deviceInfo/getDetail/${id}`)

// 新增设备信息
export const createDeviceApi = (data: DeviceDTO) =>
  request.post<DeviceApiResponse<unknown>>('/manage/api/deviceInfo/save', data)

// 更新设备信息
export const updateDeviceApi = (data: DeviceDTO) =>
  request.post<DeviceApiResponse<unknown>>('/manage/api/deviceInfo/update', data)

// 删除设备信息
export const deleteDeviceApi = (id: string) =>
  request.get<DeviceApiResponse<unknown>>(`/manage/api/deviceInfo/delete/${id}`)

// 设备状态变更
export const toggleDeviceStatusApi = (params: {
  id: string
  status: number
  scrapReason?: string
}) =>
  request.get<DeviceApiResponse<unknown>>('/manage/api/deviceInfo/enable', {
    ...params,
    scrapReason: params.scrapReason || '',
  })
