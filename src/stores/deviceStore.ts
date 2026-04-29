import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DeviceQuery, DeviceRecord, DeviceDTO } from '@/types/system/device'
import {
  pageDevicesApi,
  createDeviceApi,
  updateDeviceApi,
  deleteDeviceApi,
  toggleDeviceStatusApi,
} from '@/api/system/device'
import { ElMessage } from 'element-plus'

export const useDeviceStore = defineStore('device', () => {
  const loading = ref(false)
  const deviceList = ref<DeviceRecord[]>([])
  const total = ref(0)

  // 获取设备分页列表
  const fetchDeviceList = async (params: DeviceQuery) => {
    loading.value = true
    try {
      const res = await pageDevicesApi(params)
      // request.get<T> 返回的是 Promise<ApiResponse<T>> 也就是 { code, msg, data: T }
      // 或者 request.get<T> 在拦截器处理后返回的是 T (如果是直接返回 data)
      // 根据 workstation 的代码: res.data.records，说明 res 是 { data: { records... } }
      // 所以 pageDevicesApi 返回的是包含 data 属性的对象
      if (res && res.data) {
        deviceList.value = res.data.records || []
        total.value = res.data.total || 0
      } else {
        deviceList.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('获取设备列表失败:', error)
      deviceList.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // 新增设备
  const createDevice = async (data: DeviceDTO) => {
    loading.value = true
    try {
      const res = await createDeviceApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('新增设备成功')
        return true
      } else {
        ElMessage.error(res.msg || '新增设备失败')
        return false
      }
    } catch (error) {
      console.error('新增设备失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新设备
  const updateDevice = async (data: DeviceDTO) => {
    loading.value = true
    try {
      const res = await updateDeviceApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('更新设备成功')
        return true
      } else {
        ElMessage.error(res.msg || '更新设备失败')
        return false
      }
    } catch (error) {
      console.error('更新设备失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除设备
  const removeDevice = async (id: string) => {
    try {
      const res = await deleteDeviceApi(id)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('删除设备成功')
        return true
      } else {
        ElMessage.error(res.msg || '删除设备失败')
        return false
      }
    } catch (error) {
      console.error('删除设备失败:', error)
      return false
    }
  }

  // 变更状态
  const changeDeviceStatus = async (id: string, status: number, scrapReason?: string) => {
    try {
      const res = await toggleDeviceStatusApi({ id, status, scrapReason })
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('状态变更成功')
        return true
      } else {
        ElMessage.error(res.msg || '状态变更失败')
        return false
      }
    } catch (error) {
      console.error('状态变更失败:', error)
      return false
    }
  }

  return {
    loading,
    deviceList,
    total,
    fetchDeviceList,
    createDevice,
    updateDevice,
    removeDevice,
    changeDeviceStatus,
  }
})
