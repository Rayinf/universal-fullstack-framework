import request from '@/utils/request'

// 基础路径
const BASE_URL = '/manage/api/orderInfo'

/**
 * 任务状态映射 (前端字符 <-> 后端数字)
 * 1：待核查 2：已核查 3：待排程 4：已排程 5：已排程（待审核） 6：已排程（已审核）
 * 7：已派发 8：生产中 9：质检中 10：已完成 11：已交付 12：延迟
 */
export const STATUS_NAME_MAP: Record<string, number> = {
  待核查: 1,
  已核查: 2,
  待排程: 3,
  已提交至计划: 3,
  已排程: 4,
  '已排程（待审核）': 5,
  '已排程（已审核）': 6,
  已派发: 7,
  生产中: 8,
  质检中: 9,
  已完成: 10,
  已交付: 11,
  延迟: 12,
}

export const STATUS_VALUE_MAP: Record<number, string> = {
  1: '待核查',
  2: '已核查',
  3: '待排程',
  4: '已排程',
  5: '已排程（待审核）',
  6: '已排程（已审核）',
  7: '已派发',
  8: '生产中',
  9: '质检中',
  10: '已完成',
  11: '已交付',
  12: '延迟',
}

/**
 * 优先级映射 (前端字符 <-> 后端数字)
 * 1：高 2：中 3：低 4：紧急插单
 */
export const PRIORITY_NAME_MAP: Record<string, number> = {
  高: 1,
  中: 2,
  低: 3,
  紧急插单: 4,
}

export const PRIORITY_VALUE_MAP: Record<number, string> = {
  1: '高',
  2: '中',
  3: '低',
  4: '紧急插单',
}

// 分页查询任务
export function getTaskPageApi(params: any) {
  return request.get(`${BASE_URL}/page`, params)
}

// 通过ID查询详情
export function getTaskDetailApi(id: string | number) {
  return request.get(`${BASE_URL}/${id}`)
}

// 添加工单任务
export function saveTaskApi(data: any) {
  return request.post(`${BASE_URL}/save`, data)
}

// 编辑工单任务信息
export function updateTaskApi(data: any) {
  return request.post(`${BASE_URL}/update`, data)
}

// 工单任务核查 (状态变更)
export function approveTaskApi(id: string | number) {
  return request.post(`${BASE_URL}/approve/${id}`)
}

// 任务信息确认提交
export function submitTaskApi(id: string | number) {
  return request.get(`${BASE_URL}/taskSubmit/${id}`)
}

// 任务确认编辑 (中转修改：仅交期、优先级、备注)
export function transferModifyTaskApi(data: any) {
  return request.post(`${BASE_URL}/taskConfirmationEdit`, data)
}

// 任务核查编辑（使用 taskConfirmationEdit 接口）
export function updateTaskForReviewApi(data: any) {
  return request.post(`${BASE_URL}/taskConfirmationEdit`, data)
}

// 删除任务
export function deleteTaskApi(id: string | number) {
  return request.delete(`${BASE_URL}/${id}`)
}

// 获取文件列表
export function getTaskFilesApi(orderId: string | number) {
  return request.get(`${BASE_URL}/getFileList`, { orderId })
}

// 删除文件
export function deleteTaskFileApi(id: string | number) {
  return request.get(`${BASE_URL}/fileDelete/${id}`)
}

// 上传文件 (FormData)
export function saveTaskFileApi(data: FormData) {
  return request.post(`${BASE_URL}/saveFile`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// 获取文件预览地址 (返回真实URL)
export function getFilePreviewUrlApi(fileId: string | number) {
  return request.get<string>(`${BASE_URL}/filePreview/${fileId}`)
}

// 获取文件批量下载地址
export function batchDownloadTaskFileApi(fileIds: (string | number)[]) {
  return request.get(
    `${BASE_URL}/fileBatchDownload`,
    { fileIds: fileIds.join(',') },
    {
      responseType: 'blob',
    },
  )
}

// 获取工单任务修改历史（版本列表）
export function getTaskVersionListApi(id: string | number) {
  return request.get(`${BASE_URL}/getOrderInfoVersionList/${id}`)
}

// 获取产品列表信息
export function getProjectInfoListApi() {
  return request.get<any[]>('/manage/api/projectInfo/list')
}

/**
 * 分页查询进度信息 (甘特图数据源)
 * @param params { page: object, dto: object }
 */
export function getOrderPageForProgressApi(params: any) {
  return request.get('/manage/api/getDetailInfo/orderPageForProgress', params)
}

/**
 * 获取生产执行详情信息
 * @param orderId 订单ID
 */
export function getAllDetailInfoApi(orderId: string | number) {
  return request.post('/manage/api/getDetailInfo/getDetailInfo', { orderId })
}
