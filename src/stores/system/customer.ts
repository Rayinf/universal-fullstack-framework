import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref } from 'vue'
import {
  pageCustomersApi,
  listCustomersApi,
  saveCustomerApi,
  updateCustomerApi,
  deleteCustomerApi,
} from '@/api/system/customer'
import type { Customer, CustomerPageQuery, CustomerPageRequest } from '@/types/system/customer'
import { ElMessage } from 'element-plus'

export const useCustomerStore = defineStore('customer', () => {
  const customerList = ref<Customer[]>([])
  const loading = ref(false)
  const total = ref(0)
  const pagination = ref<CustomerPageRequest>({
    current: 1,
    size: 10,
  })

  // 获取分页列表
  const fetchCustomerPage = async (query?: CustomerPageQuery) => {
    loading.value = true
    try {
      const params = {
        sortColumn: 'create_time',
        sortType: 'desc',
        ...pagination.value,
        ...query,
      }
      const res = await pageCustomersApi(params)
      if ((res.code === 0 || res.code === 200) && res.data) {
        customerList.value = res.data.records || []
        total.value = res.data.total || 0
      } else {
        customerList.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('获取客户列表失败:', error)
      customerList.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // 获取所有客户简易列表（用于下拉选择）
  const fetchCustomerList = async () => {
    try {
      const res = await listCustomersApi()
      if ((res.code === 0 || res.code === 200) && res.data) {
        return res.data
      }
      return []
    } catch (error) {
      console.error('获取客户列表失败:', error)
      return []
    }
  }

  // 保存客户
  const saveCustomer = async (data: Partial<Customer>) => {
    loading.value = true
    try {
      const res = await saveCustomerApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('保存成功')
        return true
      }
      return false
    } catch (error) {
      console.error('保存客户失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新客户
  const updateCustomer = async (data: Partial<Customer>) => {
    loading.value = true
    try {
      const res = await updateCustomerApi(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('更新成功')
        return true
      }
      return false
    } catch (error) {
      console.error('更新客户失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除客户
  const deleteCustomer = async (id: string | number) => {
    loading.value = true
    try {
      const res = await deleteCustomerApi(id)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('删除成功')
        return true
      }
      return false
    } catch (error) {
      console.error('删除客户失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    customerList,
    loading,
    total,
    pagination,
    fetchCustomerPage,
    fetchCustomerList,
    saveCustomer,
    updateCustomer,
    deleteCustomer,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useCustomerStore, import.meta.hot))
}
