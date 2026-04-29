import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  pageBasicInfoApi,
  listBasicInfoByTypeApi,
  saveBasicInfoApi,
  updateBasicInfoApi,
  deleteBasicInfoApi,
  pageScanBindingProcessApi,
  saveScanBindingProcessApi,
  updateScanBindingProcessApi,
  deleteScanBindingProcessApi,
} from '@/api/parameter'
import type {
  BasicInfoDto,
  BasicInfoPageQuery,
  BasicInfoRecord,
  BasicInfoPageRequest,
  ScanBindingProcessDto,
  ScanBindingProcessRecord,
} from '@/types/parameter'

export const useParameterStore = defineStore('parameter', () => {
  // --- State ---
  const loading = ref(false)
  const basicInfos = ref<BasicInfoRecord[]>([])
  const total = ref(0)

  const scanBindingProcesses = ref<ScanBindingProcessRecord[]>([])
  const scanBindingTotal = ref(0)

  const assetTypes = ref<BasicInfoRecord[]>([])
  const processStepList = ref<BasicInfoRecord[]>([])

  const parseBasicInfoRecords = (payload: unknown): BasicInfoRecord[] => {
    if (Array.isArray(payload)) {
      return payload
    }

    if (payload && typeof payload === 'object') {
      const raw = payload as { records?: unknown; data?: unknown }
      if (Array.isArray(raw.records)) {
        return raw.records
      }

      if (raw.data && typeof raw.data === 'object') {
        const nested = raw.data as { records?: unknown }
        if (Array.isArray(nested.records)) {
          return nested.records
        }
      }
    }

    return []
  }

  // --- Actions ---

  // 分页查询基础信息
  const fetchBasicInfos = async (params: BasicInfoPageQuery & BasicInfoPageRequest) => {
    loading.value = true
    try {
      const res = await pageBasicInfoApi(params)
      if (res.code === 0 || res.code === 200) {
        basicInfos.value = res.data?.records || []
        total.value = res.data?.total || 0
      } else {
        ElMessage.error(res.msg || '获取列表失败')
        basicInfos.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('获取列表失败:', error)
      ElMessage.error('获取列表时发生错误')
    } finally {
      loading.value = false
    }
  }

  // 获取资产类型列表
  const fetchAssetTypes = async () => {
    try {
      // 资产类型的type为13
      // 这里复用分页接口或者列表接口，参考原代码是用分页接口取所有
      const params: BasicInfoPageQuery & BasicInfoPageRequest = {
        current: 1,
        size: 1000,
        type: 13,
        keyWord: '',
        sortColumn: 'create_time',
        sortType: 'desc',
      }
      const res = await pageBasicInfoApi(params)
      if (res.code === 0 || res.code === 200) {
        assetTypes.value = parseBasicInfoRecords(res.data)
      } else {
        assetTypes.value = []
      }
    } catch (error) {
      console.error('获取资产类型失败:', error)
      assetTypes.value = []
    }
  }

  // 获取工序列表
  const fetchProcessStepList = async () => {
    try {
      // 工序名称的type为8
      const res = await listBasicInfoByTypeApi(8)
      if (res.code === 0 || res.code === 200) {
        processStepList.value = res.data || []
      }
    } catch (error) {
      console.error('获取工序列表失败:', error)
    }
  }

  // 新增基础信息
  const createBasicInfo = async (data: BasicInfoDto) => {
    loading.value = true
    try {
      const res = await saveBasicInfoApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('创建成功')
        return true
      } else {
        ElMessage.error(res.msg || '创建失败')
        return false
      }
    } catch (error) {
      console.error('创建失败:', error)
      ElMessage.error('创建时发生错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新基础信息
  const updateBasicInfo = async (data: BasicInfoDto) => {
    loading.value = true
    try {
      const res = await updateBasicInfoApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('更新成功')
        return true
      } else {
        ElMessage.error(res.msg || '更新失败')
        return false
      }
    } catch (error) {
      console.error('更新失败:', error)
      ElMessage.error('更新时发生错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除基础信息
  const removeBasicInfo = async (id: number) => {
    try {
      const res = await deleteBasicInfoApi(id)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('删除成功')
        return true
      } else {
        ElMessage.error(res.msg || '删除失败')
        return false
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除时发生错误')
      return false
    }
  }

  // --- 扫码枪工序关联 Actions ---

  // 分页查询扫码枪工序关联
  const fetchScanBindingProcesses = async (params: Record<string, unknown>) => {
    loading.value = true
    try {
      const res = await pageScanBindingProcessApi(params)
      if (res.code === 0 || res.code === 200) {
        scanBindingProcesses.value = res.data?.records || []
        scanBindingTotal.value = res.data?.total || 0
      } else {
        ElMessage.error(res.msg || '获取列表失败')
        scanBindingProcesses.value = []
        scanBindingTotal.value = 0
      }
    } catch (error) {
      console.error('获取列表失败:', error)
      ElMessage.error('获取列表时发生错误')
    } finally {
      loading.value = false
    }
  }

  // 新增扫码枪工序关联
  const createScanBindingProcess = async (data: ScanBindingProcessDto) => {
    loading.value = true
    try {
      const res = await saveScanBindingProcessApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('创建成功')
        return true
      } else {
        ElMessage.error(res.msg || '创建失败')
        return false
      }
    } catch (error) {
      console.error('创建失败:', error)
      ElMessage.error('创建时发生错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新扫码枪工序关联
  const updateScanBindingProcess = async (data: ScanBindingProcessDto) => {
    loading.value = true
    try {
      const res = await updateScanBindingProcessApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('更新成功')
        return true
      } else {
        ElMessage.error(res.msg || '更新失败')
        return false
      }
    } catch (error) {
      console.error('更新失败:', error)
      ElMessage.error('更新时发生错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除扫码枪工序关联
  const removeScanBindingProcess = async (id: number) => {
    try {
      const res = await deleteScanBindingProcessApi(id)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('删除成功')
        return true
      } else {
        ElMessage.error(res.msg || '删除失败')
        return false
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除时发生错误')
      return false
    }
  }

  return {
    loading,
    basicInfos,
    total,
    scanBindingProcesses,
    scanBindingTotal,
    assetTypes,
    processStepList,

    fetchBasicInfos,
    fetchAssetTypes,
    fetchProcessStepList,
    createBasicInfo,
    updateBasicInfo,
    removeBasicInfo,

    fetchScanBindingProcesses,
    createScanBindingProcess,
    updateScanBindingProcess,
    removeScanBindingProcess,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useParameterStore, import.meta.hot))
}
