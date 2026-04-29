/**
 * MES系统模拟数据
 */

import { generateId, randomInt, randomPick, randomDate, formatDateTime } from './mockConfig'

// ===================== 用户相关 =====================

// 模拟用户账号 (用户名 -> 密码)
export const mockCredentials: Record<string, string> = {
  admin: 'admin123',
  zhangsan: '123456',
  lisi: '123456',
  wangwu: '123456',
  operator: '123456',
  inspector: '123456',
}

// 角色定义
export const mockRoles = [
  { id: '1', name: '系统管理员', code: 'admin' },
  { id: '2', name: '任务录入员', code: 'task_entry' },
  { id: '3', name: '计划员', code: 'planner' },
  { id: '4', name: '工艺技术员', code: 'technician' },
  { id: '5', name: '生产操作工', code: 'operator' },
  { id: '6', name: '生产管理员', code: 'production_manager' },
  { id: '7', name: '质量检验员', code: 'inspector' },
  { id: '8', name: '质量工程师', code: 'quality_engineer' },
  { id: '9', name: '质量负责人', code: 'quality_manager' },
  { id: '10', name: '售后工程师', code: 'service_engineer' },
  { id: '11', name: '部门领导', code: 'department_leader' },
]

// 模拟用户列表
export const mockUsers = [
  {
    userId: '1',
    username: 'admin',
    realName: '系统管理员',
    phone: '13800138000',
    email: 'admin@mes.com',
    avatar: null,
    deptId: '1',
    deptName: '系统管理部',
    roles: ['1'],
    status: 'active',
  },
  {
    userId: '2',
    username: 'zhangsan',
    realName: '张三',
    phone: '13800138001',
    email: 'zhangsan@mes.com',
    avatar: null,
    deptId: '2',
    deptName: '生产部',
    roles: ['2', '3'],
    status: 'active',
  },
  {
    userId: '3',
    username: 'lisi',
    realName: '李四',
    phone: '13800138002',
    email: 'lisi@mes.com',
    avatar: null,
    deptId: '3',
    deptName: '工艺部',
    roles: ['4'],
    status: 'active',
  },
  {
    userId: '4',
    username: 'wangwu',
    realName: '王五',
    phone: '13800138003',
    email: 'wangwu@mes.com',
    avatar: null,
    deptId: '2',
    deptName: '生产部',
    roles: ['5', '6'],
    status: 'active',
  },
  {
    userId: '5',
    username: 'operator',
    realName: '赵六',
    phone: '13800138004',
    email: 'zhaoliu@mes.com',
    avatar: null,
    deptId: '2',
    deptName: '生产部',
    roles: ['5'],
    status: 'active',
  },
  {
    userId: '6',
    username: 'inspector',
    realName: '钱七',
    phone: '13800138005',
    email: 'qianqi@mes.com',
    avatar: null,
    deptId: '4',
    deptName: '质量部',
    roles: ['7', '8'],
    status: 'active',
  },
]

// 部门列表
export const mockDepartments = [
  { id: '1', name: '系统管理部', parentId: null },
  { id: '2', name: '生产部', parentId: null },
  { id: '3', name: '工艺部', parentId: null },
  { id: '4', name: '质量部', parentId: null },
  { id: '5', name: '计划部', parentId: null },
  { id: '6', name: '设备部', parentId: null },
  { id: '7', name: '仓储部', parentId: null },
]

// ===================== 任务管理 =====================

// 任务状态映射 (1-12)
const taskProgressStatuses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

// 任务优先级 (1:高, 2:中, 3:低, 4:紧急插单)
const taskPriorities = [1, 2, 3, 4]

// 模拟生产任务
export const mockTasks = Array.from({ length: 25 }, (_, i) => {
  const progressStatus = randomPick(taskProgressStatuses)
  const priority = randomPick(taskPriorities)
  const createdDate = new Date()
  createdDate.setDate(createdDate.getDate() - randomInt(5, 30))

  // 计划交期应该在未来
  const deliveryDate = new Date()
  deliveryDate.setDate(deliveryDate.getDate() + randomInt(10, 60))

  // 根据状态决定是否有核查/提交信息
  const hasVerified = progressStatus >= 2
  const hasSubmitted = progressStatus >= 3

  const verifier = hasVerified ? randomPick(mockUsers).realName : undefined
  const verificationTime = hasVerified
    ? formatDateTime(new Date(createdDate.getTime() + 86400000))
    : undefined

  const submitter = hasSubmitted ? randomPick(mockUsers).realName : undefined
  const submissionTime = hasSubmitted
    ? formatDateTime(new Date(createdDate.getTime() + 172800000))
    : undefined

  const customerName = randomPick(['国科天成', '九数智汇', '某大型国企', '技术研究所'])
  const productModel = randomPick(['GT-001', 'JS-V2', 'MES-Terminal', 'Sensor-X1'])

  return {
    id: i + 100, // integer
    orderNo: `TASK-${String(i + 1).padStart(4, '0')}`,
    orderName: `${customerName}-${productModel}生产任务`,
    barcode: `BC-${Date.now()}-${i}`,
    productQuantity: randomInt(100, 1000),
    orderModel: productModel,
    customerId: randomInt(1, 5),
    customerName, // 用于前端展示
    progressStatus,
    deliveryTime: deliveryDate.toISOString().replace('T', ' ').slice(0, 19),
    contractNo: `HT-${2025000 + i}`,
    taskType: 1, // 生产任务
    remarks: randomPick(['紧急订单', '常规生产', '加急处理', '']),
    priority,
    createBy: randomInt(1, 6),
    creator: randomPick(mockUsers).realName, // 前端展示用
    createTime: formatDateTime(createdDate),
    verifier,
    verificationTime,
    submitter,
    submissionTime,
  }
})

// ===================== 计划排程 =====================

// 排程状态
export const scheduleStatuses = [
  '待排程',
  '已排程',
  '审核中',
  '审核通过',
  '审核不通过',
  '已派发',
  '执行中',
  '已完成',
  '已取消',
]

// 模拟生产线
export const mockProductionLines = [
  { id: '1', name: 'A线', capacity: 500, status: '运行中' },
  { id: '2', name: 'B线', capacity: 400, status: '运行中' },
  { id: '3', name: 'C线', capacity: 300, status: '维护中' },
  { id: '4', name: 'D线', capacity: 450, status: '运行中' },
]

// 模拟排程计划
export const mockSchedules = Array.from({ length: 15 }, (_, i) => {
  const status = randomPick(scheduleStatuses)
  const createdDate = new Date()
  createdDate.setDate(createdDate.getDate() - randomInt(3, 20))

  const planStart = new Date()
  planStart.setDate(planStart.getDate() + randomInt(1, 10))
  const planEnd = new Date(planStart)
  planEnd.setDate(planEnd.getDate() + randomInt(3, 15))

  const hasApproval = ['审核通过', '已派发', '执行中', '已完成'].includes(status)
  const hasDistribution = ['已派发', '执行中', '已完成'].includes(status)
  const hasExecution = ['执行中', '已完成'].includes(status)

  const numTasks = randomInt(1, 4)
  const taskIds = Array.from({ length: numTasks }, (_, idx) =>
    String(mockTasks[(i + idx) % mockTasks.length].id),
  )

  return {
    id: generateId(),
    scheduleCode: `SCH-${String(i + 1).padStart(4, '0')}`,
    scheduleName: `生产计划方案${i + 1}`,
    taskIds,
    productionLine: randomPick(mockProductionLines).name,
    planStartTime: formatDateTime(planStart),
    planEndTime: formatDateTime(planEnd),
    status,
    approvalStatus: hasApproval ? '审核通过' : status === '审核中' ? '审核中' : '待审核',
    distributionStatus: hasDistribution ? '已派发' : '待派发',
    executionStatus: hasExecution ? (status === '已完成' ? '已完成' : '执行中') : '待执行',
    approvalTime: hasApproval
      ? formatDateTime(new Date(createdDate.getTime() + 86400000))
      : undefined,
    distributionTime: hasDistribution
      ? formatDateTime(new Date(createdDate.getTime() + 172800000))
      : undefined,
    progress: status === '已完成' ? 100 : hasExecution ? randomInt(30, 90) : 0,
    remarks: randomPick(['常规排程', '紧急插单', '优先安排', '']),
    createdBy: randomPick(mockUsers).realName,
    createdAt: formatDateTime(createdDate),
  }
})

// ===================== 工艺技术 =====================

export const mockProducts = Array.from({ length: 10 }, (_, i) => ({
  id: generateId(),
  productCode: `PRD-${String(i + 1).padStart(3, '0')}`,
  productName: `产品${String.fromCharCode(65 + i)}`,
  productType: randomPick(['机芯', '整机', '配件', '组件']),
  specification: `规格型号-${randomInt(100, 999)}`,
  version: `V${randomInt(1, 5)}.${randomInt(0, 9)}`,
  status: randomPick(['有效', '停用', '待审核']),
  createdAt: formatDateTime(),
  updatedAt: formatDateTime(),
}))

// ===================== 生产执行 =====================

export const mockWorkOrders = Array.from({ length: 25 }, (_, i) => {
  const task = mockTasks[i % mockTasks.length]
  return {
    id: generateId(),
    workOrderCode: `WO-${String(i + 1).padStart(5, '0')}`,
    taskId: String(task.id),
    taskCode: task.orderNo,
    productName: task.orderModel,
    productionLine: randomPick(mockProductionLines).name,
    planQuantity: randomInt(50, 300),
    completedQuantity: randomInt(0, 200),
    defectQuantity: randomInt(0, 10),
    status: randomPick(['待派发', '已派发', '执行中', '已完成', '已取消']),
    planStartTime: randomDate(7) + ' 08:00:00',
    planEndTime: randomDate(3) + ' 17:00:00',
    createdAt: formatDateTime(),
  }
})

// ===================== 质量监督 =====================

export const mockInspections = Array.from({ length: 30 }, (_, i) => ({
  id: generateId(),
  inspectionCode: `INS-${String(i + 1).padStart(5, '0')}`,
  workOrderId: mockWorkOrders[i % mockWorkOrders.length].id,
  workOrderCode: mockWorkOrders[i % mockWorkOrders.length].workOrderCode,
  inspectionType: randomPick(['入厂检验', '过程检验', '成品检验', '出厂检验']),
  productName: mockWorkOrders[i % mockWorkOrders.length].productName,
  sampleQuantity: randomInt(5, 20),
  passQuantity: randomInt(3, 20),
  failQuantity: randomInt(0, 5),
  result: randomPick(['合格', '不合格', '待判定']),
  inspector: randomPick(mockUsers.filter((u) => u.roles.includes('7'))).realName,
  inspectedAt: formatDateTime(),
}))

export const mockNonconformities = Array.from({ length: 8 }, (_, i) => ({
  id: generateId(),
  ncCode: `NC-${String(i + 1).padStart(4, '0')}`,
  inspectionId: mockInspections[i].id,
  inspectionCode: mockInspections[i].inspectionCode,
  productName: mockInspections[i].productName,
  defectType: randomPick(['外观缺陷', '尺寸超差', '功能异常', '性能不达标']),
  quantity: randomInt(1, 10),
  status: randomPick(['待评审', '评审中', '待处理', '处理中', '已关闭']),
  createdAt: formatDateTime(),
}))

// ===================== 设备与工位 =====================

export const mockEquipments = [
  {
    id: '1',
    code: 'EQ001',
    name: 'SMT贴片机-1',
    type: '贴片设备',
    location: 'A线',
    status: '运行中',
  },
  {
    id: '2',
    code: 'EQ002',
    name: 'SMT贴片机-2',
    type: '贴片设备',
    location: 'A线',
    status: '运行中',
  },
]

export const mockWorkstations = [
  { id: '1', code: 'WS001', name: 'SMT工位-1', lineId: '1', lineName: 'A线', equipmentId: '1' },
  { id: '2', code: 'WS002', name: 'SMT工位-2', lineId: '1', lineName: 'A线', equipmentId: '2' },
]

// ===================== 统计数据 =====================

export const mockDashboardStats = {
  pendingTasks: randomInt(5, 20),
  todayPlans: randomInt(10, 30),
  inProduction: randomInt(3, 15),
  qualityExceptions: randomInt(0, 5),
}

export const mockProductionTrend = Array.from({ length: 7 }, (_, i) => {
  const date = new Date()
  date.setDate(date.getDate() - (6 - i))
  return {
    date: date.toISOString().split('T')[0],
    planQuantity: randomInt(800, 1200),
    actualQuantity: randomInt(700, 1100),
    passRate: randomInt(95, 100),
  }
})

export const mockCapacityUtilization = mockProductionLines.map((line) => ({
  lineName: line.name,
  capacity: line.capacity,
  utilized: randomInt(Math.floor(line.capacity * 0.6), line.capacity),
  utilizationRate: randomInt(60, 95),
}))

export const mockQualityTrend = Array.from({ length: 7 }, (_, i) => {
  const date = new Date()
  date.setDate(date.getDate() - (6 - i))
  return {
    date: date.toISOString().split('T')[0],
    inspected: randomInt(200, 500),
    passed: randomInt(190, 480),
    failed: randomInt(5, 20),
    passRate: randomInt(95, 99),
  }
})
