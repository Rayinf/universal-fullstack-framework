<template>
  <div class="gantt-chart-container">
    <!-- 工具栏 -->
    <div class="gantt-toolbar">
      <div class="left">
        <el-button-group>
          <el-button size="small" @click="zoomIn">
            <el-icon>
              <ZoomIn></ZoomIn>
            </el-icon> 放大
          </el-button>
          <el-button size="small" @click="zoomOut">
            <el-icon>
              <ZoomOut></ZoomOut>
            </el-icon> 缩小
          </el-button>
          <el-button size="small" @click="fitView">
            <el-icon>
              <FullScreen></FullScreen>
            </el-icon> 适应
          </el-button>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-tag type="success">{{ scheduleTasks.length }} 个已排程</el-tag>
        <el-tag type="warning">{{ pendingTasks.length }} 个待排程</el-tag>
      </div>
      <div class="right">
        <el-tag type="info">从任务池拖拽任务到甘特图</el-tag>
      </div>
    </div>

    <!-- 甘特图主体 -->
    <div class="gantt-main">
      <!-- 左侧资源列表 -->
      <div class="resource-panel">
        <div class="resource-header">排程任务</div>
        <div ref="resourceListRef" class="resource-list" @dragover.prevent @drop="onDropToLine($event, null)"
          @scroll="onResourceScroll">
          <div v-for="line in productionLines" :key="line.id" class="resource-item"
            :class="{ active: selectedLine === line.id, 'drop-target': dragOverLine === line.id }"
            @click="selectLine(line.id)" @dragover.prevent="onDragOverLine($event, line.id)"
            @dragleave="onDragLeaveLine" @drop="onDropToLine($event, line.id)">
            <!-- 修改：显示名称 -->
            <div class="resource-name" :title="line.name">{{ line.name }}</div>
            <!-- 修改：对于任务行，隐藏产能信息，或者显示任务状态 -->
            <div class="resource-info">
              <el-tag :type="line.status === '运行中' ? 'success' : 'info'" size="small">
                {{ line.status }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧甘特图 -->
      <div class="chart-panel" @dragover.prevent>
        <!-- 可滚动容器 -->
        <div ref="chartScrollContainerRef" class="chart-scroll-container" @dragover.prevent
          @drop="onDropToChart($event)" @scroll="onChartScroll">
          <!-- 时间刻度 -->
          <div class="timeline-header" :style="{ width: totalWidth + 'px' }">
            <div v-for="(date, index) in displayDates" :key="date" class="timeline-date"
              :class="{ weekend: isWeekend(date), today: isToday(date) }" :style="{ width: dayWidth + 'px' }">
              <div class="date-day">{{ getDayOfWeek(date) }}</div>
              <div class="date-num">{{ formatDateShort(date) }}</div>
            </div>
          </div>
          <!-- 图表区域 -->
          <div ref="chartContainerRef" class="gantt-chart-content">
            <!-- 产线行 -->
            <div v-for="line in productionLines" :key="line.id" class="chart-row" :style="{ height: rowHeight + 'px' }"
              @dragover.prevent="onDragOverChartRow($event, line.id)" @dragleave="onDragLeaveChartRow"
              @drop="onDropToChartRow($event, line.id)">
              <!-- 背景网格 -->
              <div class="row-grid" :style="{ width: totalWidth + 'px' }">
                <div v-for="(date, index) in displayDates" :key="date" class="grid-cell"
                  :class="{ weekend: isWeekend(date), today: isToday(date) }"
                  :style="{ left: index * dayWidth + 'px', width: dayWidth + 'px' }"></div>
              </div>

              <!-- 任务条 -->
              <div v-for="task in getLineTasks(line.id)" :key="task.id" class="gantt-task-bar" :class="[
                'priority-' + getPriorityClass(task.priority),
                { 'is-resizing': resizingTask?.id === task.id },
              ]" :style="getTaskBarStyle(task)" :draggable="!resizingTask" @dragstart="onTaskDragStart($event, task)"
                @dragend="onTaskDragEnd($event, task)" @click="selectTask(task)" :title="task.schedulingName">
                <!-- Resize Handles -->
                <div class="resize-handle left" @mousedown.stop.prevent="initResize($event, task, 'left')"></div>
                <div class="resize-handle right" @mousedown.stop.prevent="initResize($event, task, 'right')"></div>

                <div class="task-bar-content">
                  <!-- 优先显示 schedulingName，如果没有则显示 orderNo -->
                  <span class="task-label">{{ task.schedulingName || task.orderNo }}</span>
                  <span class="task-duration">{{ task.duration }}天</span>
                </div>
                <!-- 交期警告 -->
                <div v-if="isOverdue(task)" class="overdue-indicator" title="超期">!</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 滚动指示器 -->
        <div class="scroll-indicator" v-if="displayDates.length < 30">
          <el-icon>
            <ArrowRight></ArrowRight>
          </el-icon>
        </div>
      </div>
    </div>

    <!-- 任务池 -->
    <div class="task-pool">
      <div class="pool-header">
        <span class="pool-title">待排程任务池 (可拖拽排程)</span>
        <el-tag type="info">{{ pendingTasks.length }} 个任务</el-tag>
      </div>
      <div class="pool-tasks">
        <div v-for="task in pendingTasks" :key="task.id" class="pool-task-card" draggable="true"
          @dragstart="onTaskPoolDragStart($event, task)" @dragend="onDragEnd">
          <div class="task-header">
            <span class="task-code">{{ task.orderNo }}</span>
            <el-tag :type="getPriorityType(task.priority)" size="small">{{ task.priority }}</el-tag>
          </div>
          <div class="task-body">
            <div class="task-row">
              <span class="label">产品:</span>
              <span class="value" :title="task.productName">{{
                task.productName || task.orderModel || '-'
                }}</span>
            </div>
            <div class="task-row" v-if="task.productNo">
              <span class="label">编号:</span>
              <span class="value">{{ task.productNo }}</span>
            </div>
            <div class="task-row">
              <span class="label">数量:</span>
              <span class="value">{{ task.productQuantity }}</span>
            </div>
            <div class="task-row">
              <span class="label">交期:</span>
              <span class="value" :class="{ 'near-due': isNearDue(task.deliveryTime) }">
                {{ formatDateShort(task.deliveryTime) }}
              </span>
            </div>
          </div>
          <div class="task-footer">
            <span class="customer">{{ task.customerName }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务详情弹窗 (支持编辑) -->
    <el-dialog v-model="taskDialogVisible" title="排程详情调整" width="500px">
      <div v-if="selectedTask" class="task-detail">
        <el-form label-width="100px">
          <el-form-item label="任务编号">
            <span>{{ selectedTask.orderNo }}</span>
          </el-form-item>
          <el-form-item label="排程名称">
            <el-input v-model="editingTaskForm.schedulingName" />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-date-picker v-model="editingTaskForm.startDate" type="datetime" value-format="YYYY-MM-DD HH:mm:ss"
              format="YYYY-MM-DD HH:mm" style="width: 100%" @change="onDialogDateChange" />
          </el-form-item>
          <el-form-item label="工期 (小时)">
            <el-input-number v-model="editingTaskForm.duration" :min="1" :max="2400" @change="onDialogDurationChange" />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker v-model="editingTaskForm.endDate" type="datetime" value-format="YYYY-MM-DD HH:mm:ss"
              format="YYYY-MM-DD HH:mm" style="width: 100%" @change="onDialogEndDateChange" />
          </el-form-item>
        </el-form>

        <div class="task-actions" style="margin-top: 20px; justify-content: flex-end; gap: 10px">
          <el-button @click="taskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTaskEdit">保存修改</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { ZoomIn, ZoomOut, FullScreen, ArrowRight } from '@element-plus/icons-vue'

interface Task {
  id: string
  orderId?: string
  orderNo: string
  productName?: string
  productNo?: string
  orderModel: string
  customerName: string
  productQuantity: number
  priority: string
  deliveryTime: string
}

interface ProductionLine {
  id: string
  name: string
  capacity: number
  status: string
}

interface ScheduleTask {
  id: string
  orderId?: string // 对应后端 orderId
  orderNo: string
  productName?: string
  productNo?: string
  schedulingName?: string // 新增：排程名称
  resource: string
  resourceName: string
  startDate: string
  endDate: string
  duration: number
  priority: string
  deliveryTime: string
  offset: number // 相对今天的天数偏移
}

const props = defineProps<{
  productionLines: ProductionLine[]
  pendingTasks: Task[]
  scheduleTasks: ScheduleTask[]
}>()

const emit = defineEmits<{
  'update:tasks': [tasks: ScheduleTask[]]
  'task-drop': [data: { task: Task; lineId: string; date: string; offset: number }]
}>()

// 状态
const selectedLine = ref<string>('')
const dragOverLine = ref<string>('')
const dragOverChartRow = ref<string>('')
const selectedTask = ref<ScheduleTask | null>(null)
const taskDialogVisible = ref(false)

// 视图参数
const dayWidth = ref(50) // 每天的像素宽度
const rowHeight = ref(60) // 每行高度
const chartContainerRef = ref<HTMLElement>()
const chartScrollContainerRef = ref<HTMLElement>()
const resourceListRef = ref<HTMLElement>()

// 内部处理滚动同步
let isScrollingResource = false
let isScrollingChart = false

const onResourceScroll = () => {
  if (isScrollingChart) return
  isScrollingResource = true
  if (resourceListRef.value && chartScrollContainerRef.value) {
    chartScrollContainerRef.value.scrollTop = resourceListRef.value.scrollTop
  }
  setTimeout(() => (isScrollingResource = false), 50)
}

const onChartScroll = () => {
  if (isScrollingResource) return
  isScrollingChart = true
  if (resourceListRef.value && chartScrollContainerRef.value) {
    resourceListRef.value.scrollTop = chartScrollContainerRef.value.scrollTop
  }
  setTimeout(() => (isScrollingChart = false), 50)
}

// 所有显示的任务
const allTasks = computed(() => props.scheduleTasks)

// 显示的日期范围
const displayDates = computed(() => {
  const dates: string[] = []

  // 找出所有任务的最早和最晚日期
  let minDate = new Date()
  let maxDate = new Date()
  maxDate.setDate(maxDate.getDate() + 30) // 默认显示未来30天

  if (props.scheduleTasks.length > 0) {
    const startDates = props.scheduleTasks
      .map((t) => new Date(t.startDate).getTime())
      .filter((t) => !isNaN(t))
    const endDates = props.scheduleTasks
      .map((t) => new Date(t.endDate).getTime())
      .filter((t) => !isNaN(t))

    if (startDates.length > 0) {
      minDate = new Date(Math.min(...startDates))
    }
    if (endDates.length > 0) {
      maxDate = new Date(Math.max(...endDates))
    }
  }

  // 向前扩展5天,向后扩展10天作为缓冲区
  const startDate = new Date(minDate)
  startDate.setDate(startDate.getDate() - 5)

  const endDate = new Date(maxDate)
  endDate.setDate(endDate.getDate() + 10)

  // 生成日期序列 - 使用本地日期而非UTC
  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    dates.push(toLocalDateString(d))
  }

  return dates
})

const totalWidth = computed(() => displayDates.value.length * dayWidth.value)

const getPriorityClass = (priority: string) => {
  const map: Record<string, string> = {
    紧急插单: 'urgent',
    高: 'high',
    中: 'medium',
    低: 'low',
  }
  return map[priority] || 'medium'
}

const getLineTaskCount = (lineId: string) => {
  return allTasks.value.filter((t) => t.resource === lineId).length
}

const getLineTasks = (lineId: string) => {
  return allTasks.value.filter((t) => t.resource === lineId)
}

const isWeekend = (date: string) => {
  const d = new Date(date)
  const day = d.getDay()
  return day === 0 || day === 6
}

const isToday = (date: string) => {
  const today = toLocalDateString(new Date())
  return date === today
}

const isNearDue = (date: string) => {
  const due = new Date(date).getTime()
  const now = new Date().getTime()
  const daysLeft = Math.ceil((due - now) / (1000 * 60 * 60 * 24))
  return daysLeft <= 3 && daysLeft >= 0
}

const formatDateShort = (date: string) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const getDayOfWeek = (date: string) => {
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const d = new Date(date)
  return days[d.getDay()]
}

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    紧急插单: 'danger',
    高: 'warning',
    中: 'primary',
    低: 'info',
  }
  return map[priority] || 'info'
}

// 统一的日期格式化函数:将Date对象转换为本地日期字符串(YYYY-MM-DD)
const toLocalDateString = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 统一的日期时间格式化函数:将Date对象转换为本地日期时间字符串(YYYY-MM-DD HH:mm:ss)
const toLocalISO = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const isOverdue = (task: ScheduleTask) => {
  const delivery = new Date(task.deliveryTime).getTime()
  const end = new Date(task.endDate).getTime()
  return end > delivery
}

// 拖拽与缩放逻辑
const resizingTask = ref<ScheduleTask | null>(null)
const resizeDeltaX = ref(0) // 实时像素偏移量
let resizeState = {
  startX: 0,
  startLeft: 0,
  startWidth: 0,
  originalStart: 0, // timestamp
  originalEnd: 0, // timestamp
  originalDuration: 0,
  direction: '' as 'left' | 'right',
}

// ... (keep editingTaskForm and selectTask) ...

const getTaskBarStyle = (task: ScheduleTask) => {
  // 1. 基础定位计算 (非拖拽状态)
  // 修正解析逻辑: 如果已有时间点则不追加 T00:00:00
  const parseDate = (dStr: string) => {
    if (!dStr) return new Date()
    if (dStr.includes(' ') || dStr.includes('T')) {
      return new Date(dStr.replace(' ', 'T'))
    }
    return new Date(dStr + 'T00:00:00')
  }

  const firstDate = parseDate(displayDates.value[0])
  const taskStart = parseDate(task.startDate)

  const diffTime = taskStart.getTime() - firstDate.getTime()
  const baseLeft = (diffTime / (1000 * 60 * 60 * 24)) * dayWidth.value
  const baseWidth = task.duration * dayWidth.value - 4

  // 2. 如果是正在调整大小的任务,返回实时预览样式
  if (resizingTask.value && resizingTask.value.id === task.id) {
    let newWidth = resizeState.startWidth
    let newLeft = resizeState.startLeft

    if (resizeState.direction === 'right') {
      newWidth = Math.max(dayWidth.value * 0.1, resizeState.startWidth + resizeDeltaX.value)
    } else {
      const minWidth = dayWidth.value * 0.1
      const potentialWidth = resizeState.startWidth - resizeDeltaX.value
      const potentialLeft = resizeState.startLeft + resizeDeltaX.value

      if (potentialWidth >= minWidth) {
        newWidth = potentialWidth
        newLeft = potentialLeft
      } else {
        newWidth = minWidth
        newLeft = resizeState.startLeft + (resizeState.startWidth - minWidth)
      }
    }

    return {
      left: newLeft + 'px',
      width: newWidth + 'px',
      zIndex: 100,
    }
  }

  // 3. 常规返回
  return {
    left: baseLeft + 'px',
    width: baseWidth + 'px',
  }
}

const initResize = (event: MouseEvent, task: ScheduleTask, direction: 'left' | 'right') => {
  // 1. 先计算准确的样式值
  const style = getTaskBarStyle(task)
  const currentLeft = parseFloat(style.left as string)
  const currentWidth = parseFloat(style.width as string)

  // 2. 设置初始状态
  const parseDate = (dStr: string) => {
    if (dStr.includes(' ') || dStr.includes('T')) {
      return new Date(dStr.replace(' ', 'T'))
    }
    return new Date(dStr + 'T00:00:00')
  }

  resizeState = {
    startX: event.clientX,
    startLeft: currentLeft,
    startWidth: currentWidth,
    originalStart: parseDate(task.startDate).getTime(),
    originalEnd: parseDate(task.endDate).getTime(),
    originalDuration: task.duration,
    direction,
  }

  // 3. 最后设置 resizingTask
  resizingTask.value = task
  resizeDeltaX.value = 0

  window.addEventListener('mousemove', doResize)
  window.addEventListener('mouseup', stopResize)
}

const doResize = (event: MouseEvent) => {
  if (!resizingTask.value) return
  resizeDeltaX.value = event.clientX - resizeState.startX
}

const stopResize = () => {
  window.removeEventListener('mousemove', doResize)
  window.removeEventListener('mouseup', stopResize)

  if (resizingTask.value) {
    const deltaDays = resizeDeltaX.value / dayWidth.value

    if (Math.abs(deltaDays) > 0.01) {
      const oneDay = 24 * 3600 * 1000
      const task = resizingTask.value

      if (resizeState.direction === 'right') {
        const newDuration = Math.max(0.1, resizeState.originalDuration + deltaDays)
        task.duration = parseFloat(newDuration.toFixed(2))

        const sDate = new Date(task.startDate.replace(' ', 'T'))
        const eDate = new Date(sDate.getTime() + newDuration * oneDay)
        task.endDate = toLocalISO(eDate)
      } else {
        const maxDelta = resizeState.originalDuration - 0.1
        const safeDelta = Math.min(deltaDays, maxDelta)

        const newStart = new Date(resizeState.originalStart + safeDelta * oneDay)
        const newStartDateStr = toLocalISO(newStart)

        if (newStartDateStr !== resizingTask.value.startDate) {
          task.startDate = newStartDateStr
          task.duration = parseFloat((resizeState.originalDuration - safeDelta).toFixed(2))

          const firstDate = new Date(displayDates.value[0] + 'T00:00:00')
          const diffTime = newStart.getTime() - firstDate.getTime()
          task.offset = diffTime / oneDay
        }
      }

      const updatedTasks = props.scheduleTasks.map((t) => (t.id === task.id ? { ...task } : t))
      emit('update:tasks', updatedTasks)
    }

    resizingTask.value = null
    resizeDeltaX.value = 0
  }
}
// 编辑逻辑
const editingTaskForm = reactive({
  schedulingName: '',
  startDate: '',
  endDate: '',
  duration: 0,
})

const onDialogDateChange = () => {
  if (editingTaskForm.startDate && editingTaskForm.duration) {
    const start = new Date(editingTaskForm.startDate)
    // editingTaskForm.duration是小时数
    const end = new Date(start.getTime() + editingTaskForm.duration * 3600 * 1000)
    editingTaskForm.endDate = toLocalISO(end)
  }
}

const onDialogDurationChange = () => {
  onDialogDateChange()
}

const onDialogEndDateChange = () => {
  if (editingTaskForm.startDate && editingTaskForm.endDate) {
    const start = new Date(editingTaskForm.startDate).getTime()
    const end = new Date(editingTaskForm.endDate).getTime()
    const hours = (end - start) / (3600 * 1000)
    if (hours > 0) editingTaskForm.duration = parseFloat(hours.toFixed(1))
  }
}

const saveTaskEdit = () => {
  if (!selectedTask.value) return

  // 更新本地对象
  selectedTask.value.schedulingName = editingTaskForm.schedulingName
  selectedTask.value.startDate = editingTaskForm.startDate
  selectedTask.value.endDate = editingTaskForm.endDate

  // Duration in task model is DAYS. Convert hours back to days.
  selectedTask.value.duration = Math.ceil(editingTaskForm.duration / 24)
  // Note: This loses precision if we want sub-day rendering on the Gantt.
  // But Gantt rendering `width = task.duration * dayWidth` implies duration is days.
  // If I want sub-day, I should use float duration.
  // Let's use float.
  selectedTask.value.duration = parseFloat((editingTaskForm.duration / 24).toFixed(2))

  // 触发更新事件
  const updatedTasks = props.scheduleTasks.map((t) =>
    t.id === selectedTask.value!.id ? { ...selectedTask.value! } : t,
  )
  emit('update:tasks', updatedTasks)
  taskDialogVisible.value = false
  ElMessage.success('已更新排程信息')
}

// ...

const selectLine = (lineId: string) => {
  selectedLine.value = lineId
}

// Also fix selectTask to populate duration correctly (Calculate hours precisely)
const selectTask = (task: ScheduleTask) => {
  selectedTask.value = task
  editingTaskForm.schedulingName = task.schedulingName || task.orderNo

  // 确保传入的是 YYYY-MM-DD HH:mm:ss 格式
  const formatForPicker = (dStr: string) => {
    if (!dStr) return ''
    return dStr.replace('T', ' ')
  }

  editingTaskForm.startDate = formatForPicker(task.startDate)
  editingTaskForm.endDate = formatForPicker(task.endDate)

  // 精确计算小时数
  const start = new Date(task.startDate.replace(' ', 'T')).getTime()
  const end = new Date(task.endDate.replace(' ', 'T')).getTime()
  const hours = (end - start) / (3600 * 1000)
  editingTaskForm.duration = hours > 0 ? parseFloat(hours.toFixed(1)) : 0

  taskDialogVisible.value = true
}

// 拖拽功能 (Drag Whole Task)
const draggedTask = ref<Task | null>(null)
const draggedGanttTask = ref<ScheduleTask | null>(null)
// 新增：记录拖拽开始时鼠标相对于任务条左边缘的偏移量
const dragStartXOffset = ref(0)

// 从任务池拖拽开始
const onTaskPoolDragStart = (event: DragEvent, task: Task) => {
  console.log('Pool drag start:', task.orderNo)
  draggedTask.value = task
  draggedGanttTask.value = null // 清空甘特图任务
  dragStartXOffset.value = 0
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', task.id)
    // 设置拖拽图像
    event.dataTransfer.setDragImage(event.target as Element, 0, 0)
  }
}

// 甘特图内任务拖拽开始
const onTaskDragStart = (event: DragEvent, task: ScheduleTask) => {
  // 保存原始甘特图任务
  draggedGanttTask.value = task

  // 计算鼠标点击位置相对于任务条左侧的偏移
  if (event.target instanceof HTMLElement) {
    const rect = event.target.getBoundingClientRect()
    dragStartXOffset.value = event.clientX - rect.left
  } else {
    dragStartXOffset.value = 0
  }

  // 将 ScheduleTask 转换为 Task 格式以兼容拖拽逻辑
  draggedTask.value = {
    id: task.id,
    orderId: task.orderId,
    orderNo: task.orderNo,
    orderModel: '',
    customerName: '',
    productQuantity: 0,
    priority: task.priority,
    deliveryTime: task.deliveryTime,
  }
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', task.id)
  }
}

const onTaskDragEnd = (_event: DragEvent, _task: ScheduleTask) => {
  // 任务拖拽结束，清理状态
  // 注意：这个函数主要用于 DOM 拖拽结束的清理
  // 真正的数据更新逻辑在 drop 处理函数中
  draggedTask.value = null
  draggedGanttTask.value = null
  dragStartXOffset.value = 0
}

const onDragEnd = () => {
  console.log('Drag end, draggedTask was:', draggedTask.value?.orderNo)
  draggedTask.value = null
  draggedGanttTask.value = null
  dragOverLine.value = ''
  dragOverChartRow.value = ''
}

// 计算拖拽放置的日期 (Fix: Adjust for dragStartXOffset)
const getDropDate = (event: DragEvent): string | null => {
  if (!chartScrollContainerRef.value) return null

  const chartRect = chartScrollContainerRef.value.getBoundingClientRect()
  const scrollLeft = chartScrollContainerRef.value.scrollLeft || 0

  // 修正：计算的是任务条左边缘应该落在哪一列，而不是鼠标落在哪一列
  // 实际落点X = 鼠标X - 拖拽偏移量 - 容器左边缘 + 滚动距离
  // 如果是任务池拖拽(dragStartXOffset=0)，则鼠标位置即为落点
  const offsetOverride = draggedGanttTask.value ? dragStartXOffset.value : 0
  const adjustedX = event.clientX - offsetOverride - chartRect.left + scrollLeft

  const dayIndex = Math.floor(adjustedX / dayWidth.value)

  if (dayIndex >= 0 && dayIndex < displayDates.value.length) {
    return displayDates.value[dayIndex]
  }
  return null
}

const getOffsetFromToday = (dateStr: string) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const date = new Date(dateStr)
  date.setHours(0, 0, 0, 0)
  return Math.round((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
}

// 拖拽悬停
const onDragOverLine = (event: DragEvent, lineId: string) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
  dragOverLine.value = lineId
}

const onDragLeaveLine = () => {
  dragOverLine.value = ''
}

const onDragOverChartRow = (event: DragEvent, lineId: string) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
  dragOverChartRow.value = lineId
}

const onDragLeaveChartRow = () => {
  dragOverChartRow.value = ''
}

// 放置到产线(默认从今天开始,工期5天)
const onDropToLine = (event: DragEvent, lineId: string | null) => {
  event.preventDefault()
  event.stopPropagation()

  if (!draggedTask.value || !lineId) return

  const line = props.productionLines.find((l) => l.id === lineId)
  if (!line) return

  // 创建新排程任务 - 使用本地日期
  const today = new Date()
  const startDate = toLocalDateString(today)

  // 判断是甘特图内拖拽还是从任务池拖拽
  if (draggedGanttTask.value) {
    // 甘特图内拖拽 - 更新现有任务
    const endDate = new Date(today)
    endDate.setDate(endDate.getDate() + draggedGanttTask.value.duration)

    const updatedTasks = props.scheduleTasks.map((t) => {
      if (t.id === draggedGanttTask.value!.id) {
        return {
          ...t,
          resource: lineId,
          resourceName: line.name,
          startDate,
          endDate: toLocalDateString(endDate),
          offset: 0,
        }
      }
      return t
    })
    emit('update:tasks', updatedTasks)
    ElMessage.success(`已将 ${draggedTask.value.orderNo} 移动到 ${line.name}`)
  } else {
    // 从任务池拖拽 - 触发事件让父组件处理
    emit('task-drop', {
      task: draggedTask.value,
      lineId,
      date: startDate,
      offset: 0,
    })
  }

  draggedTask.value = null
  draggedGanttTask.value = null
  dragOverLine.value = ''
}

const onDropToChartRow = (event: DragEvent, lineId: string) => {
  event.preventDefault()
  event.stopPropagation()

  if (!draggedTask.value) return

  const dropDate = getDropDate(event)
  if (!dropDate) return

  const line = props.productionLines.find((l) => l.id === lineId)
  if (!line) return

  // 计算偏移量
  const offset = getOffsetFromToday(dropDate)

  // 判断是甘特图内拖拽还是从任务池拖拽
  if (draggedGanttTask.value) {
    // 甘特图内拖拽 - 更新现有任务
    // 保持原有的开始时间点(时分秒), 仅改变日期
    const originalTimeStr = draggedGanttTask.value.startDate.includes(' ')
      ? draggedGanttTask.value.startDate.split(' ')[1]
      : '08:00:00'

    const newStartDate = `${dropDate} ${originalTimeStr}`

    // 根据工期计算结束时间
    const startMs = new Date(newStartDate.replace(' ', 'T')).getTime()
    const durationMs = draggedGanttTask.value.duration * 24 * 3600 * 1000
    const newEndDate = toLocalISO(new Date(startMs + durationMs))

    const updatedTasks = props.scheduleTasks.map((t) => {
      if (t.id === draggedGanttTask.value!.id) {
        return {
          ...t,
          resource: lineId,
          resourceName: line.name,
          startDate: newStartDate,
          endDate: newEndDate,
          offset: offset,
        }
      }
      return t
    })
    emit('update:tasks', updatedTasks)
    ElMessage.success(`已移动任务到新的位置`)
  } else {
    // 从任务池拖拽 - 触发事件让父组件处理
    emit('task-drop', {
      task: draggedTask.value,
      lineId,
      date: `${dropDate} 08:00:00`,
      offset,
    })
  }

  draggedTask.value = null
  draggedGanttTask.value = null
  dragOverChartRow.value = ''
}

const onDropToChart = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()

  // 默认放置到第一个产线
  if (props.productionLines.length > 0) {
    onDropToChartRow(event, props.productionLines[0].id)
  }
}

// 缩放操作
const zoomIn = () => {
  dayWidth.value = Math.min(dayWidth.value * 1.2, 80)
}

const zoomOut = () => {
  dayWidth.value = Math.max(dayWidth.value / 1.2, 30)
}

const fitView = () => {
  dayWidth.value = 50
}

onMounted(() => {
  // 初始化
})

onUnmounted(() => {
  // 清理
})
</script>

<style scoped>
.gantt-chart-container {
  height: 600px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
}

.gantt-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #ebeef5;
  background: linear-gradient(135deg, #f5f7fa 0%, #fafafa 100%);
}

.gantt-toolbar .left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gantt-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  background: #fff;
}

.resource-panel {
  width: 180px;
  /* 稍微加宽，适应长部门名 */
  border-right: 1px solid #ebeef5;
  background: #fcfcfc;
  display: flex;
  flex-direction: column;
  z-index: 20;
  box-shadow: 4px 0 8px rgba(0, 0, 0, 0.02);
}

.resource-header {
  height: 50px;
  padding: 0 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  background: #fafafa;
  color: #1d1d1f;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
  box-sizing: border-box;
}

.resource-list {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none;
  /* 隐藏资源列表滚动条，通过甘特图控制 */
}

.resource-list::-webkit-scrollbar {
  display: none;
}

.resource-item {
  height: 60px;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-sizing: border-box;
}

.resource-item:hover {
  background: #f5f7fa;
}

.resource-item.active {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.resource-item.drop-target {
  background: #f6ffed;
  border-left: 3px solid #52c41a;
}

.resource-name {
  font-weight: 600;
  font-size: 13px;
  color: #262626;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resource-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.capacity {
  font-size: 11px;
  color: #8c8c8c;
}

.line-task-count {
  font-size: 11px;
  color: #bfbfbf;
}

.chart-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.chart-scroll-container {
  flex: 1;
  overflow: auto;
  /* 允许双向滚动 */
  position: relative;
  scroll-behavior: smooth;
}

.timeline-header {
  display: flex;
  height: 50px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 30;
}

.timeline-date {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #f0f0f0;
  font-size: 12px;
}

.timeline-date.weekend {
  background: #fafafa;
}

.timeline-date.today {
  background: #e6f7ff;
  position: relative;
}

.timeline-date.today::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #1890ff;
}

.date-day {
  font-size: 10px;
  color: #8c8c8c;
  margin-bottom: 2px;
}

.date-num {
  font-size: 12px;
  font-weight: 600;
  color: #262626;
}

.gantt-chart-content {
  position: relative;
  width: max-content;
  /* 确保内容宽度正确 */
  min-width: 100%;
}

.chart-row {
  position: relative;
  border-bottom: 1px solid #f0f0f0;
  box-sizing: border-box;
}

.chart-row:hover {
  background: #fafafa;
}

.row-grid {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  pointer-events: none;
  display: flex;
}

.grid-cell {
  height: 100%;
  border-right: 1px solid #f0f0f0;
  box-sizing: border-box;
  flex-shrink: 0;
}

.grid-cell.weekend {
  background: rgba(0, 0, 0, 0.01);
}

.grid-cell.today {
  background: rgba(24, 144, 255, 0.02);
}

.gantt-task-bar {
  position: absolute;
  top: 14px;
  /* (60 - 32) / 2 */
  height: 32px;
  border-radius: 4px;
  cursor: grab;
  display: flex;
  align-items: center;
  padding: 0 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  /* 移除 width/left 的 transition 以保证缩放流畅 */
  z-index: 10;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.gantt-task-bar:hover {
  z-index: 100;
}

.gantt-task-bar.is-resizing {
  transition: none !important;
  z-index: 200;
  box-shadow: 0 0 0 2px #409eff;
}

.resize-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: ew-resize;
  z-index: 20;
  opacity: 0;
  transition: opacity 0.2s;
  background: rgba(0, 0, 0, 0.1);
}

.gantt-task-bar:hover .resize-handle {
  opacity: 1;
}

.resize-handle.left {
  left: 0;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.resize-handle.right {
  right: 0;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

.gantt-task-bar:active {
  cursor: grabbing;
}

.gantt-task-bar.priority-urgent {
  background: #ff4d4f;
  color: #fff;
}

.gantt-task-bar.priority-high {
  background: #fa8c16;
  color: #fff;
}

.gantt-task-bar.priority-medium {
  background: #1890ff;
  color: #fff;
}

.gantt-task-bar.priority-low {
  background: #8c8c8c;
  color: #fff;
}

.task-bar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-size: 11px;
  font-weight: 500;
}

.task-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-duration {
  font-size: 10px;
  opacity: 0.8;
  margin-left: 4px;
}

.overdue-indicator {
  position: absolute;
  right: 4px;
  top: 2px;
  color: #ff0000;
  font-weight: bold;
  animation: blink 1s infinite;
}

@keyframes blink {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.3;
  }
}

.task-pool {
  height: 200px;
  border-top: 2px solid #ebeef5;
  background: linear-gradient(180deg, #fafafa 0%, #f5f7fa 100%);
}

.pool-header {
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  background: rgba(230, 247, 255, 0.3);
}

.pool-title {
  font-weight: bold;
  color: #409eff;
}

.pool-tasks {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px;
  overflow-y: auto;
  align-content: flex-start;
}

.pool-task-card {
  width: 180px;
  min-height: 100px;
  padding: 12px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
}

.pool-task-card:hover {
  border-color: #409eff;
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.15);
  transform: translateY(-3px);
}

.pool-task-card:active {
  cursor: grabbing;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.task-code {
  font-weight: 600;
  font-size: 13px;
  color: #1d1d1f;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 4px;
}

.task-body {
  margin-bottom: 8px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-row {
  display: flex;
  align-items: center;
  font-size: 11px;
  line-height: 1.4;
}

.task-row .label {
  color: #86868b;
  width: 35px;
  flex-shrink: 0;
}

.task-row .value {
  color: #424245;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-row .value.near-due {
  color: #e6a23c;
  font-weight: bold;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 4px;
  border-top: 1px dashed #ebeef5;
  flex-shrink: 0;
}

.customer {
  font-size: 10px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-detail {
  padding: 10px 0;
}

.task-actions {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}

.scroll-indicator {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(64, 158, 255, 0.1);
  padding: 8px;
  border-radius: 50%;
  color: #409eff;
  animation: pulse 2s infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 0.5;
  }

  50% {
    opacity: 1;
  }
}
</style>
