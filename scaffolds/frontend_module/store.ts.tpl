import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  page__MODULE_PASCAL__Api,
  create__MODULE_PASCAL__Api,
  update__MODULE_PASCAL__Api,
  delete__MODULE_PASCAL__Api,
} from '@/api/__API_DIR__/__MODULE_CAMEL__'
import type {
  __MODULE_PASCAL__PageParams,
  __MODULE_PASCAL__Record,
  __MODULE_PASCAL__SaveDto,
} from '@/types/__TYPE_DIR__/__MODULE_CAMEL__'

export const use__MODULE_PASCAL__Store = defineStore('__MODULE_CAMEL__', () => {
  const recordList = ref<__MODULE_PASCAL__Record[]>([])
  const loading = ref(false)
  const total = ref(0)
  const pagination = ref<__MODULE_PASCAL__PageParams>({
    current: 1,
    size: 10,
  })

  const fetch__MODULE_PASCAL__Page = async (query?: Partial<__MODULE_PASCAL__PageParams>) => {
    loading.value = true
    try {
      const res = await page__MODULE_PASCAL__Api({
        current: pagination.value.current,
        size: pagination.value.size,
        ...query,
      })
      if ((res.code === 0 || res.code === 200) && res.data) {
        recordList.value = res.data.records || []
        total.value = res.data.total || 0
      } else {
        recordList.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('获取__MODULE_TAG__列表失败:', error)
      recordList.value = []
      total.value = 0
      ElMessage.error('加载__MODULE_TAG__列表失败')
    } finally {
      loading.value = false
    }
  }

  const create__MODULE_PASCAL__ = async (data: __MODULE_PASCAL__SaveDto) => {
    loading.value = true
    try {
      const res = await create__MODULE_PASCAL__Api(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('新增成功')
        return true
      }
      ElMessage.error(res.msg || '新增失败')
      return false
    } catch (error) {
      console.error('新增__MODULE_TAG__失败:', error)
      ElMessage.error('新增失败，请稍后重试')
      return false
    } finally {
      loading.value = false
    }
  }

  const update__MODULE_PASCAL__ = async (id: string, data: __MODULE_PASCAL__SaveDto) => {
    loading.value = true
    try {
      const res = await update__MODULE_PASCAL__Api(id, data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('更新成功')
        return true
      }
      ElMessage.error(res.msg || '更新失败')
      return false
    } catch (error) {
      console.error('更新__MODULE_TAG__失败:', error)
      ElMessage.error('更新失败，请稍后重试')
      return false
    } finally {
      loading.value = false
    }
  }

  const delete__MODULE_PASCAL__ = async (id: string) => {
    loading.value = true
    try {
      const res = await delete__MODULE_PASCAL__Api(id)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('删除成功')
        return true
      }
      ElMessage.error(res.msg || '删除失败')
      return false
    } catch (error) {
      console.error('删除__MODULE_TAG__失败:', error)
      ElMessage.error('删除失败，请稍后重试')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    recordList,
    loading,
    total,
    pagination,
    fetch__MODULE_PASCAL__Page,
    create__MODULE_PASCAL__,
    update__MODULE_PASCAL__,
    delete__MODULE_PASCAL__,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(use__MODULE_PASCAL__Store, import.meta.hot))
}
