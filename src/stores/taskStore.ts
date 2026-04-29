/**
 * 任务管理 Store
 * 管理生产任务的状态 and 数据 - 对接后端 orderInfo 接口
 * 对应需求规格书 SRS-FUNC-0002
 */

import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref, computed } from 'vue'
import request from '../utils/request'
import {
  getTaskPageApi,
  getTaskDetailApi,
  saveTaskApi,
  updateTaskApi,
  updateTaskForReviewApi,
  approveTaskApi,
  submitTaskApi,
  transferModifyTaskApi,
  deleteTaskApi,
  STATUS_NAME_MAP,
  STATUS_VALUE_MAP,
  PRIORITY_NAME_MAP,
  PRIORITY_VALUE_MAP,
  getTaskFilesApi,
  deleteTaskFileApi,
  getTaskVersionListApi,
} from '../api/task'
import type {
  Task,
  TaskFormData,
  TaskStatus,
  TaskPriority,
  TaskFilterParams,
  TaskFilterOptions,
  TaskTransferModifyData,
  TaskAttachment,
} from '../types/task'

export const useTaskStore = defineStore('task', () => {
  // 任务列表
  const taskList = ref<Task[]>([])
  // 当前选中的任务
  const currentTask = ref<Task | null>(null)
  // 当前任务的文件列表
  const currentTaskFiles = ref<TaskAttachment[]>([])
  // 加载状态
  const loading = ref(false)
  // 分页信息
  const pagination = ref({
    current: 1,
    size: 10,
    total: 0,
  })

  // 筛选选项
  const filterOptions = ref<TaskFilterOptions>({
    customers: [],
    productModels: [],
    priorities: ['高', '中', '低', '紧急插单'],
    statuses: [
      '待核查',
      '已核查',
      '待排程',
      '已排程',
      '已排程（待审核）',
      '已排程（已审核）',
      '已派发',
      '生产中',
      '质检中',
      '已完成',
      '已交付',
      '延迟',
    ],
  })

  // 各状态任务数量统计（独立存储，不依赖当前taskList）
  const statusCounts = ref<Record<string, number>>({
    待核查: 0,
    已核查: 0,
    待排程: 0,
    已排程: 0,
    '已排程（待审核）': 0,
    '已排程（已审核）': 0,
    已派发: 0,
    生产中: 0,
    质检中: 0,
    已完成: 0,
    已交付: 0,
    延迟: 0,
  })

  // 待处理任务 (待核查 + 已核查)
  const pendingTasks = computed(() =>
    taskList.value.filter((t) => t.status === '待核查' || t.status === '已核查'),
  )

  // 刷新所有状态的统计数据（用于初始化badge显示）
  const fetchStatusCounts = async () => {
    try {
      // 并发请求各个状态的总数
      const statuses: Array<{ key: string; value: number }> = [
        { key: '待核查', value: 1 },
        { key: '已核查', value: 2 },
      ]

      const promises = statuses.map(async (status) => {
        const response: any = await getTaskPageApi({
          current: 1,
          size: 1, // 只需要获取total，不需要数据
          progressStatus: status.value,
          sortColumn: 'create_time',
          sortType: 'desc',
        })
        return {
          status: status.key,
          count: response.code === 0 || response.code === 200 ? response.data.total : 0,
        }
      })

      const results = await Promise.all(promises)
      results.forEach((result) => {
        statusCounts.value[result.status] = result.count
      })
    } catch (error) {
      console.error('获取状态统计失败:', error)
    }
  }

  /**
   * 后端 VO 转换为前端 Task 对象
   */
  const mapVoToTask = (vo: any): Task => {
    // 处理字符串类型的 progressStatus
    const statusValue =
      vo.progressStatus !== null && vo.progressStatus !== undefined
        ? parseInt(String(vo.progressStatus))
        : 1

    // 处理 priority (1-4)
    const priorityValue =
      vo.priority !== null && vo.priority !== undefined ? parseInt(String(vo.priority)) : 2

    return {
      id: String(vo.id),
      taskCode: vo.orderNo || '',
      taskName: vo.orderName || '',
      barcode: vo.barcode || '',
      contractNo: vo.contractNo || '',
      customerId: String(vo.customerId || ''),
      customerName: vo.customerName || vo.creator || '未知客户',
      productName: vo.productName || '',
      productNo: vo.productNo || '',
      productModel: vo.orderModel || '',
      plannedQuantity: vo.productQuantity || 0,
      plannedDeliveryDate: vo.deliveryTime ? vo.deliveryTime.split(' ')[0].split('T')[0] : '',
      priority: (PRIORITY_VALUE_MAP[priorityValue] as TaskPriority) || '中',
      status: (STATUS_VALUE_MAP[statusValue] as TaskStatus) || '待核查',
      taskType: vo.taskType || 1,
      createdBy:
        vo.creator || vo.realName || vo.updater || vo.modifier || String(vo.createBy || ''),
      createdAt: vo.createTime ? vo.createTime.replace('T', ' ') : '',
      remarks: vo.remarks || '',
      processRouteId: vo.processRouteId ? String(vo.processRouteId) : '',
      progress: statusValue >= 10 ? 100 : statusValue * 10,
      version: vo.version || '',
      actualStartTime: vo.actualStartTime ? vo.actualStartTime.replace('T', ' ') : '',
      actualEndTime: vo.actualEndTime ? vo.actualEndTime.replace('T', ' ') : '',
      verifier: vo.verifier || '',
      verificationTime: vo.verifierTime ? vo.verifierTime.replace('T', ' ') : '',
      updatedBy: vo.updater || vo.realName || vo.creator || String(vo.updateBy || ''),
      orderInfoHistoryDOList: vo.orderInfoHistoryDOList || [],
      attachments: [],
    }
  }

  // 获取任务列表
  const fetchTasks = async (params?: TaskFilterParams) => {
    loading.value = true
    try {
      const queryParams = {
        current: pagination.value.current,
        size: pagination.value.size,
        keyword: params?.keyword,
        progressStatus: params?.status ? STATUS_NAME_MAP[params.status] : undefined,
        priority: params?.priority ? PRIORITY_NAME_MAP[params.priority] : undefined,
        contractNo: params?.keyword,
        startDate: params?.deliveryDateRange?.[0],
        endDate: params?.deliveryDateRange?.[1],
        sortColumn: 'create_time',
        sortType: 'desc',
      }

      const response: any = await getTaskPageApi(queryParams)

      // 成功码按 0 或 200 判断
      if ((response.code === 0 || response.code === 200) && response.data) {
        taskList.value = (response.data.records || []).map(mapVoToTask)
        pagination.value = {
          current: response.data.current,
          size: response.data.size,
          total: response.data.total,
        }

        // 如果查询时指定了status，更新对应状态的计数
        if (params?.status && statusCounts.value[params.status] !== undefined) {
          statusCounts.value[params.status] = response.data.total
        }
      }
    } catch (error) {
      console.error('获取任务列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取任务详情
  const fetchTaskById = async (id: string) => {
    loading.value = true
    try {
      const response: any = await getTaskDetailApi(id)
      if ((response.code === 0 || response.code === 200) && response.data) {
        const task = mapVoToTask(response.data)
        currentTask.value = task
        return task
      }
      return null
    } catch (error) {
      console.error('获取任务详情失败:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  // 创建任务
  const createTask = async (data: TaskFormData) => {
    loading.value = true
    try {
      const payload = {
        orderNo: data.taskCode,
        orderName: data.taskName,
        productName: data.productName,
        productNo: data.productNo,
        productQuantity: data.plannedQuantity,
        orderModel: data.productModel,
        customerId: Number(data.customerId),
        progressStatus: 1,
        deliveryTime: data.plannedDeliveryDate ? data.plannedDeliveryDate + ' 00:00:00' : undefined,
        contractNo: data.contractNo,
        taskType: 1, // 生产任务
        remarks: data.remarks,
        priority: PRIORITY_NAME_MAP[data.priority] || 2,
        barcode: data.barcode,
      }

      const response: any = await saveTaskApi(payload)
      if (response.code === 0 || response.code === 200) {
        // 修正：强制刷新第一页，确保能找到最新创建的任务（按时间倒序）
        pagination.value.current = 1
        await fetchTasks()

        let returnData = response.data ? mapVoToTask(response.data) : null

        // 如果后端没有返回有效ID（例如返回了 null 或 id 为空），尝试通过 taskCode 在列表中查找
        if (!returnData || !returnData.id || returnData.id === 'undefined') {
          const found = taskList.value.find((t) => t.taskCode === data.taskCode)
          if (found) {
            returnData = found
          }
        }

        return { success: true, data: returnData }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('创建任务失败:', error)
      return { success: false, message: error.message || '创建失败' }
    } finally {
      loading.value = false
    }
  }

  // 更新任务（通用）
  const updateTask = async (id: string, data: Partial<TaskFormData>) => {
    loading.value = true
    try {
      const oldResponse: any = await getTaskDetailApi(id)
      if (!(oldResponse.code === 0 || oldResponse.code === 200))
        return { success: false, message: '获取原数据失败' }

      const oldData = oldResponse.data

      // 如果当前状态是待核查（status=1），则使用 updateTaskApi（全量更新）
      // 注意：这里需要根据后端实际逻辑调整。如果任务核查页面的编辑也需要走 taskConfirmationEdit，请修改此处逻辑。
      // 根据用户最新指示：任务核查的编辑调 taskConfirmationEdit 接口
      // 通常"任务录入"阶段的全量编辑（包括产品信息等）使用 updateTaskApi
      // "任务核查"阶段的编辑可能受限。
      // 我们需要判断当前是在哪个模块调用。
      // 为了不破坏原有逻辑，我们可以新增一个专门用于核查阶段编辑的方法，或者在 updateTask 内部判断。
      // 鉴于用户明确指出“任务核查的编辑”，我们可以在 TaskReview.vue 中调用一个新的 action，或者修改 updateTask。

      // 这里我们保持 updateTask 为全量更新（用于 TaskEntry），新增 updateTaskForReview 用于核查页。
      const payload = {
        ...oldData,
        orderName: data.taskName ?? oldData.orderName,
        productName: data.productName ?? oldData.productName,
        productNo: data.productNo ?? oldData.productNo,
        productQuantity: data.plannedQuantity ?? oldData.productQuantity,
        orderModel: data.productModel ?? oldData.orderModel,
        customerId: data.customerId ? Number(data.customerId) : oldData.customerId,
        deliveryTime: data.plannedDeliveryDate
          ? data.plannedDeliveryDate + ' 00:00:00'
          : oldData.deliveryTime,
        contractNo: data.contractNo ?? oldData.contractNo,
        remarks: data.remarks ?? oldData.remarks,
        priority: data.priority ? PRIORITY_NAME_MAP[data.priority] : oldData.priority,
        barcode: data.barcode ?? oldData.barcode,
      }

      const response: any = await updateTaskApi(payload)
      if (response.code === 0 || response.code === 200) {
        await fetchTasks()
        return { success: true, data: mapVoToTask(response.data || {}) }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('更新任务失败:', error)
      return { success: false, message: error.message || '更新失败' }
    } finally {
      loading.value = false
    }
  }

  // 任务核查阶段的编辑 (受限更新：交期、优先级、备注)
  // 使用 taskConfirmationEdit 接口
  const updateTaskReview = async (id: string, data: Partial<TaskFormData>) => {
    loading.value = true
    try {
      const payload = {
        id: Number(id),
        deliveryTime: data.plannedDeliveryDate ? data.plannedDeliveryDate + ' 00:00:00' : undefined,
        priority: data.priority ? PRIORITY_NAME_MAP[data.priority] : undefined,
        remarks: data.remarks,
      }
      const response: any = await updateTaskForReviewApi(payload)
      if (response.code === 0 || response.code === 200) {
        await fetchTasks()
        return { success: true }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('核查编辑失败:', error)
      return { success: false, message: error.message || '编辑失败' }
    } finally {
      loading.value = false
    }
  }

  // 核查任务
  const reviewTask = async (id: string) => {
    loading.value = true
    try {
      const response: any = await approveTaskApi(id)
      if (response.code === 0 || response.code === 200) {
        await fetchTasks()
        // 刷新统计数据
        await fetchStatusCounts()
        return { success: true }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('核查任务失败:', error)
      return { success: false, message: error.message || '核查失败' }
    } finally {
      loading.value = false
    }
  }

  // 提交到计划
  const submitTaskToPlan = async (id: string) => {
    loading.value = true
    try {
      const response: any = await submitTaskApi(id)
      if (response.code === 0 || response.code === 200) {
        await fetchTasks()
        // 刷新统计数据
        await fetchStatusCounts()
        return { success: true }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('提交失败:', error)
      return { success: false, message: '提交失败' }
    } finally {
      loading.value = false
    }
  }

  // 中转修改
  const transferModifyTask = async (id: string, data: TaskTransferModifyData) => {
    loading.value = true
    try {
      const payload = {
        id: Number(id),
        deliveryTime: data.plannedDeliveryDate ? data.plannedDeliveryDate + ' 00:00:00' : undefined,
        priority: data.priority ? PRIORITY_NAME_MAP[data.priority] : undefined,
        remarks: data.remarks,
      }
      const response: any = await transferModifyTaskApi(payload)
      if (response.code === 0 || response.code === 200) {
        await fetchTasks()
        return { success: true }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      return { success: false, message: '修改失败' }
    } finally {
      loading.value = false
    }
  }

  // 删除任务
  const deleteTask = async (id: string) => {
    loading.value = true
    try {
      const response: any = await deleteTaskApi(id)
      if (response.code === 0 || response.code === 200) {
        await fetchTasks()
        // 刷新统计数据
        await fetchStatusCounts()
        return { success: true }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('删除任务失败:', error)
      return { success: false, message: error.message || '删除失败' }
    } finally {
      loading.value = false
    }
  }

  // 关联订单与工艺路线
  const associateOrderProcessRoute = async (orderId: string, processRouteId: string) => {
    try {
      const res = await request.post('/manage/api/orderInfo/addOrderProcessRoute', null, {
        params: {
          orderId,
          processRouteId,
        },
      })
      if (res.code === 0 || res.code === 200) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error: any) {
      console.error('关联工艺路线失败:', error)
      return { success: false, message: '关联工艺路线失败' }
    }
  }

  // 批量核查
  const batchReview = async (ids: string[]) => {
    loading.value = true
    try {
      let successCount = 0
      for (const id of ids) {
        const res = await reviewTask(id)
        if (res.success) successCount++
      }
      // 刷新统计数据
      await fetchStatusCounts()
      return { success: true, count: successCount }
    } catch (error: any) {
      console.error('批量核查失败:', error)
      return { success: false, message: '批量核查失败' }
    } finally {
      loading.value = false
    }
  }

  // 批量提交到计划
  const batchSubmitToPlan = async (ids: string[]) => {
    loading.value = true
    try {
      let successCount = 0
      for (const id of ids) {
        const res = await submitTaskToPlan(id)
        if (res.success) successCount++
      }
      // 刷新统计数据
      await fetchStatusCounts()
      return { success: true, count: successCount }
    } catch (error: any) {
      console.error('批量提交失败:', error)
      return { success: false, message: '批量提交失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取任务文件列表
  const fetchTaskFiles = async (orderId: string) => {
    try {
      const response: any = await getTaskFilesApi(orderId)
      if ((response.code === 0 || response.code === 200) && response.data) {
        currentTaskFiles.value = response.data
        return response.data
      }
      return []
    } catch (error) {
      console.error('获取文件列表失败:', error)
      return []
    }
  }

  // 删除任务文件
  const deleteTaskFile = async (fileId: string) => {
    try {
      const response: any = await deleteTaskFileApi(fileId)
      if (response.code === 0 || response.code === 200) {
        return { success: true }
      }
      return { success: false, message: response.msg }
    } catch (error: any) {
      console.error('删除文件失败:', error)
      return { success: false, message: '删除失败' }
    }
  }

  // 获取任务修改历史（版本列表）
  const fetchTaskHistory = async (id: string) => {
    try {
      const response: any = await getTaskVersionListApi(id)
      if ((response.code === 0 || response.code === 200) && response.data) {
        const historyList = response.data.orderInfoHistoryDOList || []
        const currentVO = response.data.orderInfoVO

        // 映射历史记录
        const mappedHistory = historyList.map((vo: any) => {
          const task = mapVoToTask(vo)
          // 对于历史记录，修改时间应该是 updateTime
          if (vo.updateTime) {
            task.createdAt = vo.updateTime.replace('T', ' ')
          }
          return task
        })

        // 如果有当前版本，也可以加入列表（通常作为最新的一条）
        if (currentVO) {
          const currentTask = mapVoToTask(currentVO)
          if (currentVO.updateTime) {
            currentTask.createdAt = currentVO.updateTime.replace('T', ' ')
          }
          // 避免重复（如果历史列表已经包含了当前版本）
          const isDuplicate = mappedHistory.some((h: any) => h.version === currentTask.version)
          if (!isDuplicate) {
            mappedHistory.push(currentTask)
          }
        }

        // 按时间倒序排序
        return mappedHistory.sort(
          (a: any, b: any) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
        )
      }
      return []
    } catch (error) {
      console.error('获取修改历史失败:', error)
      return []
    }
  }

  return {
    taskList,
    currentTask,
    currentTaskFiles,
    loading,
    pagination,
    filterOptions,
    statusCounts,
    pendingTasks,
    fetchTasks,
    fetchTaskById,
    fetchStatusCounts,
    createTask,
    updateTask,
    updateTaskReview,
    deleteTask,
    reviewTask,
    batchReview,
    submitTaskToPlan,
    batchSubmitToPlan,
    transferModifyTask,
    associateOrderProcessRoute,
    fetchTaskFiles,
    deleteTaskFile,
    fetchTaskHistory,
    mapVoToTask,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useTaskStore, import.meta.hot))
}
