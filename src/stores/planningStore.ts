/**
 * 计划排程管理 Store (SRS-FUNC-0003)
 */

import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref, computed } from 'vue'
import * as planningApi from '@/api/planning'
import type {
  OrderInfoVO,
  OrderSchedulingVO,
  OrderSchedulingUpdateDTO,
  OrderSchedulingQueryDTO,
  OrderSchedulingForwardQueryDTO,
  OrderSchedulingExecuteQueryDTO,
  OrderSchedulingDistributeSaveDTO,
  ExecutionTaskVO,
} from '@/api/planning'

export const usePlanningStore = defineStore('planning', () => {
  // State
  const scheduleList = ref<OrderSchedulingVO[]>([])
  const currentSchedule = ref<OrderSchedulingVO | null>(null)
  const pendingTasks = ref<OrderInfoVO[]>([]) // 待排程任务
  const executionTasks = ref<ExecutionTaskVO[]>([]) // 待执行任务
  const loading = ref(false)
  const pagination = ref({
    current: 1,
    size: 10,
    total: 0,
  })

  // Computed
  const statusCounts = computed(() => {
    const counts: Record<number, number> = {}
    scheduleList.value.forEach((schedule) => {
      if (schedule.reviewStatus !== undefined) {
        counts[schedule.reviewStatus] = (counts[schedule.reviewStatus] || 0) + 1
      }
    })
    return counts
  })

  const pendingApprovalSchedules = computed(() =>
    scheduleList.value.filter(
      (s) => s.reviewStatus === 1 || s.reviewStatus === 2, // 1: 待审核 2：审核中
    ),
  )

  const approvedSchedules = computed(() =>
    scheduleList.value.filter(
      (s) => s.reviewStatus === 3, // 3：审核通过
    ),
  )

  // Actions
  async function fetchSchedules(params?: OrderSchedulingForwardQueryDTO) {
    loading.value = true
    try {
      const response = await planningApi.getAlreadyScheduledList({
        current: pagination.value.current,
        size: pagination.value.size,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      })

      if (response.code === 0 || response.code === 200) {
        // 后端返回的是数组格式，不是分页格式
        scheduleList.value = response.data || []
        pagination.value.total = scheduleList.value.length
        return { success: true }
      }
      return { success: false, message: response.msg || '获取排程列表失败' }
    } catch (error) {
      console.error('获取排程列表失败:', error)
      return { success: false, message: '获取排程列表失败' }
    } finally {
      loading.value = false
    }
  }

  async function fetchPendingTasks(params?: OrderSchedulingQueryDTO) {
    loading.value = true
    try {
      const response = await planningApi.getPendingTaskPage({
        current: pagination.value.current,
        size: pagination.value.size,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      })

      if (response.code === 0 || response.code === 200) {
        pendingTasks.value = response.data.records
        pagination.value.total = response.data.total
        return { success: true }
      }
      return { success: false, message: response.msg || '获取待排程任务失败' }
    } catch (error) {
      console.error('获取待排程任务失败:', error)
      return { success: false, message: '获取待排程任务失败' }
    } finally {
      loading.value = false
    }
  }

  async function fetchExecuteTasks(params?: OrderSchedulingExecuteQueryDTO) {
    loading.value = true
    try {
      const response = await planningApi.getExecutePage({
        current: pagination.value.current,
        size: pagination.value.size,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      })

      if (response.code === 0 || response.code === 200) {
        executionTasks.value = response.data.records
        pagination.value.total = response.data.total
        return { success: true }
      }
      return { success: false, message: response.msg || '获取待执行任务失败' }
    } catch (error) {
      console.error('获取待执行任务失败:', error)
      return { success: false, message: '获取待执行任务失败' }
    } finally {
      loading.value = false
    }
  }

  /**
   * 辅助函数：确保返回的是 ID 字符串而非对象
   */
  function ensureId(val: any): string {
    if (!val) return ''
    if (typeof val === 'object' && val.id) return String(val.id)
    return String(val)
  }

  async function createSchedule(data: OrderSchedulingUpdateDTO) {
    loading.value = true
    try {
      // 防御性处理：确保 orderId 和 id 都是纯字符串 ID
      // 关键逻辑：如果传入的 data 中没有 id，但有 orderId，且该 orderId 对应的待排程任务有 orderScheduledId，则使用 orderScheduledId 作为 id
      let updateId = data.id
      if (!updateId && data.orderId) {
        // 尝试从 pendingTasks 中查找是否有对应的 orderScheduledId
        const pendingTask = pendingTasks.value.find((t) => t.id === ensureId(data.orderId))
        if (pendingTask && pendingTask.orderScheduledId) {
          updateId = pendingTask.orderScheduledId
        }
      }

      const payload = {
        ...data,
        id: ensureId(updateId), // 使用处理后的 ID
        orderId: data.orderId ? ensureId(data.orderId) : undefined,
        reviewStatus: data.reviewStatus, // 显式传递
      }
      const response = await planningApi.updateOrderScheduling(payload)
      if (response.code === 0 || response.code === 200) {
        return { success: true }
      }
      return { success: false, message: response.msg || '创建排程失败' }
    } catch (error) {
      console.error('创建排程失败:', error)
      return { success: false, message: '创建排程失败' }
    } finally {
      loading.value = false
    }
  }

  // 批量排程
  async function batchCreateSchedule(taskIds: any[], baseData: Partial<OrderSchedulingUpdateDTO>) {
    loading.value = true
    let successCount = 0
    let lastError = ''

    try {
      for (const rawId of taskIds) {
        const orderId = ensureId(rawId)

        // 查找是否已存在排程 ID
        let updateId = undefined
        const pendingTask = pendingTasks.value.find((t) => t.id === orderId)
        if (pendingTask && pendingTask.orderScheduledId) {
          updateId = pendingTask.orderScheduledId
        }

        const data: OrderSchedulingUpdateDTO = {
          ...baseData,
          id: updateId, // 传入排程ID
          orderId,
          reviewStatus: 1, // 待审核
        }
        const res = await planningApi.updateOrderScheduling(data)
        if (res.code === 0 || res.code === 200) {
          successCount++
        } else {
          lastError = res.msg || '部分任务排程失败'
        }
      }

      await fetchPendingTasks()
      return {
        success: successCount === taskIds.length,
        message:
          successCount === taskIds.length
            ? '批量排程成功'
            : `成功 ${successCount} 个，失败 ${taskIds.length - successCount} 个: ${lastError}`,
      }
    } catch (error) {
      console.error('批量排程失败:', error)
      return { success: false, message: '批量排程过程中发生错误' }
    } finally {
      loading.value = false
    }
  }

  async function approveSchedule(schedule: OrderSchedulingVO, status: number) {
    loading.value = true
    try {
      // 这里的逻辑需要调用 updateOrderScheduling 来更新状态
      // 关键修正：使用 orderScheduledId 作为更新接口的 id 参数
      const updateId = schedule.orderScheduledId ? String(schedule.orderScheduledId) : schedule.id

      const response = await planningApi.updateOrderScheduling({
        id: updateId,
        orderId: schedule.orderId ? ensureId(schedule.orderId) : schedule.id, // 确保 orderId 存在
        schedulingName: schedule.schedulingName, // 传递排程名称
        reviewStatus: status,
      })

      if (response.code === 0 || response.code === 200) {
        await fetchSchedules()
        return { success: true }
      }
      return { success: false, message: response.msg || '审核操作失败' }
    } catch (error) {
      console.error('审核操作失败:', error)
      return { success: false, message: '审核操作失败' }
    } finally {
      loading.value = false
    }
  }

  async function distributeSchedule(
    schedulingId: string,
    distributeItems: OrderSchedulingDistributeSaveDTO[],
  ) {
    loading.value = true
    try {
      const response = await planningApi.distribute({
        schedulingId,
        orderSchedulingDistributeSaveDTOList: distributeItems,
      })

      if (response.code === 0 || response.code === 200) {
        await fetchSchedules()
        return { success: true }
      }
      return { success: false, message: response.msg || '派发失败' }
    } catch (error) {
      console.error('派发失败:', error)
      return { success: false, message: '派发失败' }
    } finally {
      loading.value = false
    }
  }

  async function confirmCompletion(data: any) {
    loading.value = true
    try {
      const response = await planningApi.confirmCompletion(data)
      if (response.code === 0 || response.code === 200) {
        await fetchExecuteTasks()
        return { success: true }
      }
      return { success: false, message: response.msg || '确认完工失败' }
    } catch (error) {
      console.error('确认完工失败:', error)
      return { success: false, message: '确认完工失败' }
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    scheduleList,
    currentSchedule,
    pendingTasks,
    executionTasks,
    loading,
    pagination,

    // Computed
    statusCounts,
    pendingApprovalSchedules,
    approvedSchedules,

    // Actions
    fetchSchedules,
    fetchPendingTasks,
    fetchExecuteTasks,
    createSchedule,
    batchCreateSchedule,
    approveSchedule,
    distributeSchedule,
    confirmCompletion,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePlanningStore, import.meta.hot))
}
