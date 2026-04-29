// 产品信息 (后端API数据结构)
export interface ProductInfo {
  id: number
  productName: string
  productNo: string
  productCategory: number // 分类信息：产品系列、产品类别
  productModel: string
  progressStatus: number // 1：有效 2：试产 3：停产
  remarks: string
  createBy: number
  createTime: string
  updateBy?: number
  updateTime?: string
  isDeleted?: number
}

// 产品信息分页查询DTO
export interface ProductQueryDTO {
  productNo?: string
  productCategory?: number
  keyword?: string
  progressStatus?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: 'asc' | 'desc'
}

// 产品信息保存/编辑DTO
export interface ProductSaveDTO {
  id?: number
  productName: string
  productNo: string
  productCategory: number
  productModel: string
  progressStatus: number
  remarks?: string
  createBy?: number
  createTime?: string
}

// 产品信息 (前端使用的扩展类型,兼容旧代码)
export interface Product {
  id: string
  productCode: string
  productName: string
  productModel: string
  productSeries: string
  productCategory: string
  status: '有效' | '试产' | '停产'
  description: string
  processIds: string[]
  createdBy: string
  createdAt: string
  updatedAt: string
}

// 工序信息
export interface Process {
  id: string
  processCode: string
  processName: string
  description: string
  isKeyProcess: boolean
  isEnabled: boolean
  isReferenced: boolean // 是否已被工艺路线引用
  createdBy: string
  createdAt: string
  updatedAt: string
}

// 工艺路线工序
export interface RouteProcess {
  id: string
  processId: string
  processCode: string
  processName: string
  sequenceNumber: number
  isKeyProcess: boolean
  responsibleTeam: string
  description: string
  fileIds: string[]
  fileNames?: string[] // 关联的文件名称
}

// 产品工艺路线
export interface ProcessRoute {
  id: string
  routeCode: string
  routeName: string
  productId: string
  productName: string
  version: string
  status: '草稿' | '审核中' | '生效' | '已停用'
  processes: RouteProcess[]
  createdBy: string
  createdAt: string
  updatedAt: string
  publishedAt?: string
  baseRouteId?: string // 复制的源路线ID
}

// 工艺文件类型
export type DocumentType = '作业指导书' | '安全规范' | '注意事项' | '工艺图纸' | '测试规范'

// 工艺文件状态
export type DocumentStatus = '草稿' | '已发布' | '已停用'

// 工艺文件
export interface Document {
  id: string
  fileName: string
  fileType: DocumentType
  version: string
  relatedProcessId: string
  relatedProcessName: string
  status: DocumentStatus
  filePath: string
  fileSize: number
  uploadedBy: string
  uploadedAt: string
  publishedAt?: string
  previewUrl?: string // 预览URL
}

// 委外设计文件
export interface OutsourcedDocument {
  id: string
  fileName: string
  originalFileNo: string
  fileType: '图纸' | '模型' | '规格书' | '其他'
  supplierName: string
  version: string
  status: '草稿' | '已发布' | '已停用'
  relatedProcessId: string
  relatedProcessName: string
  filePath: string
  fileSize: number
  uploadedBy: string
  uploadedAt: string
  previewUrl?: string
}

// 测试规范状态
export type TestSpecStatus = '草稿' | '已发布' | '已停用'

// 测试阶段
export type TestStage = '入厂检' | '过程检' | '出厂检' | '型式试验'

// 测试项
export interface TestItem {
  id: string
  itemName: string
  itemCode: string
  testMethod: string
  referenceFile: string
  criteria: string
  criteriaType: '数值型' | '定性型'
  minValue?: number
  maxValue?: number
  unit?: string
}

// 测试规范
export interface TestSpecification {
  id: string
  specName: string
  specCode: string
  applicableObject: string
  testStage: TestStage
  version: string
  status: TestSpecStatus
  testItems: TestItem[]
  createdBy: string
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

// 文件版本历史
export interface DocumentVersion {
  id: string
  documentId: string
  documentType: 'Document' | 'OutsourcedDocument' | 'TestSpecification'
  version: string
  filePath: string
  revisionNote: string
  revisedBy: string
  revisedAt: string
  previousVersionId?: string
  fileContent?: string // 用于版本对比
}

// 筛选条件
export interface ProductFilter {
  keyword: string
  productSeries: string
  productCategory: string
  status: string
  dateRange: [string, string] | null
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

export interface DocumentFilter {
  keyword: string
  fileType: string
  status: string
  processId: string
}

// 审批流程
export interface ApprovalNode {
  id: string
  nodeName: string
  approverRole: string
  approverId?: string
  status: '待审批' | '已通过' | '已拒绝'
  approvalTime?: string
  approvalComment?: string
  sequenceNumber: number
}

export interface ApprovalFlow {
  id: string
  targetType: 'ProcessRoute' | 'Document' | 'TestSpecification'
  targetId: string
  targetName: string
  status: '审核中' | '已通过' | '已拒绝'
  initiator: string
  initiatedAt: string
  nodes: ApprovalNode[]
  completedAt?: string
}

// 操作日志
export interface OperationLog {
  id: string
  userId: string
  userName: string
  operation: string
  module: string
  targetId: string
  targetName: string
  details: Record<string, any>
  ipAddress?: string
  createdAt: string
}

// 通知
export interface Notification {
  id: string
  userId: string
  title: string
  content: string
  type: 'info' | 'warning' | 'success' | 'error'
  relatedId?: string
  relatedType?: string
  isRead: boolean
  createdAt: string
  readAt?: string
}

// 待办任务
export interface TodoTask {
  id: string
  userId: string
  taskType: '审批' | '文件确认' | '工艺准备' | '物料确认'
  title: string
  description: string
  relatedId: string
  relatedType: string
  priority: '高' | '中' | '低'
  status: '待处理' | '处理中' | '已完成' | '已取消'
  dueDate?: string
  createdAt: string
  completedAt?: string
}

// 产品编码规则
export interface ProductCodeRule {
  id: string
  productSeries: string
  productCategory: string
  prefix: string
  sequenceLength: number
  currentSequence: number
}

// 用户权限
export interface UserPermission {
  userId: string
  permissions: string[]
  role: string
}

// 文件上传响应
export interface FileUploadResponse {
  success: boolean
  filePath: string
  fileName: string
  fileSize: number
  fileUrl?: string
}

// ==========================================
// 工艺库 (Process Library) 三层结构定义
// ==========================================

// Level 3: 参数 (Param)
export interface ProcessLibraryItemParam {
  id: string
  itemParamValueId?: string | number // 填报值的唯一ID (用于更新)
  paramName: string
  paramType: 1 | 2 // 1:表头字段, 2:列表字段
  jsonConfig?: any // 修改为 any, 兼容字符串和解析后的对象
  paramValue?: any // 接口返回的实际数值
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  // 前端辅助字段
  dataType?: string
  isRequired?: boolean
}

// Level 2: 表单分组 (Item)
export interface ProcessLibraryItem {
  id: string
  processLibraryItemName: string
  remarks: string
  jsonConfig?: string // 表单设计器配置 (JSON string)
  processLibraryId?: string // 新增
  complex?: number | null // 1: 单个表单, 2: 支持多表单填写
  // 注意：某些接口返回 items 时可能不包含 params，需要额外获取或通过详情接口获取
  params?: ProcessLibraryItemParam[]
  createBy?: string
  createTime?: string
}

// Level 1: 工序/工艺库 (Library)
export interface ProcessLibrary {
  id: string
  processName: string
  processCode: string
  isKey: 0 | 1
  processStatus: 1 | 2
  approvalFlowId?: string
  approvalStatus?: number
  // 某些接口可能直接返回 items
  items?: ProcessLibraryItem[]
  createBy?: string
  createTime?: string
  creator?: string
}

// DTOs for API
export interface ProcessLibrarySaveDTO {
  id?: string
  processName: string
  processCode: string
  isKey: number
  processStatus: number
}

export interface ProcessLibraryItemSaveDTO {
  id?: string
  processLibraryItemName: string
  remarks: string
  jsonConfig?: string
  complex?: number | null
}

export interface ProcessLibraryItemParamSaveDTO {
  id?: string
  paramName: string
  paramType: number
  jsonConfig?: string
}

// 关联中间表 DTO (Level 1 <-> Level 2)
export interface ProcessLibraryItemMiddleDTO {
  processLibraryId: string
  processLibraryItemMiddleDOList: {
    processLibraryItemId: string
  }[]
}

// 参数批量保存 DTO (Level 2 <-> Level 3)
export interface ProcessLibraryItemParamBatchSaveDTO {
  processLibraryItemId: string
  processLibraryItemParamSaveDTOList: ProcessLibraryItemParamSaveDTO[]
}

// ==========================================
// 工艺路线 (Process Route)
// ==========================================

export interface RoutFlowInfo {
  id?: string
  processRouteId?: string
  processLibraryId: string
  processName: string
  processIndex: number
  createTime?: string
  createBy?: string
  creator?: string
  isDeleted?: number
}

export interface ProcessRouteInfo {
  id: string
  processRouteName: string
  projectInfoId: string
  processStatus: number // 0:草稿, 1:生效, 等
  createBy?: string
  creator?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  isDeleted?: number
  // 详情接口可能带回来的工序列表
  routFlowInfos?: RoutFlowInfo[]
}

export interface ProcessRouteSaveDTO {
  id?: string
  processRouteName: string
  projectInfoId: string
  processStatus: number
}

export interface ProcessRouteUpdateDTO extends ProcessRouteSaveDTO {
  id: string
}

// ==========================================
// 作业指导书 (Work Instruction)
// ==========================================

export interface WorkInstructionInfo {
  id: string
  originalFileName: string
  fileType: number // 1:操作指南 2:安全规范 3:注意事项等
  version: string
  fileStatus: number // 1:草稿 2:已发布 3:已停用
  dataMark: string
  suffixName: string
  fileName: string
  bucketName: string
  remark: string
  createBy: string
  creator: string
  createTime: string
  updateBy: string
  updateTime: string
  isDeleted: number
  files?: string // 修改为 string
  // 关联信息
  processLibraryIds?: number[]
  processLibraryItemIds?: number[]
  processLibraryName?: string
}

export interface WorkInstructionSaveDTO {
  id?: string
  originalFileName: string
  fileType: number
  version?: string
  fileStatus?: number
  dataMark?: string
  suffixName?: string
  fileName?: string
  bucketName?: string
  remark?: string
  files?: string | File // Allow File object for FormData upload
  processLibraryIds?: number[]
  processLibraryItemIds?: number[]
  processLibraryName?: string
}

export interface WorkInstructionUpdateDTO extends WorkInstructionSaveDTO {
  revisedContent?: string
  changeReason?: string
  changePeople?: string
  changeTime?: string
  libraryWorkInstructionFileId?: string
}

export interface WorkInstructionQueryDTO {
  keyword?: string
  fileType?: number
  fileStatus?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: 'asc' | 'desc'
  current?: number
  size?: number
}

// ==========================================
// 委外设计文件 (Outsourced Document)
// ==========================================

// 字段结构与 WorkInstructionInfo 保持一致
export interface OutsourcedDocumentInfo {
  id: string
  originalFileName: string // 统一使用 originalFileName
  fileType: number // 1:图纸 2:模型 3:规格书 4:其他
  version: string
  fileStatus: number // 1:草稿 2:已发布 3:已停用
  remark: string
  suffixName: string
  fileName: string // 存储文件名
  bucketName: string
  createBy: string
  creator: string
  createTime: string
  updateBy: string
  updateTime: string
  isDeleted: number
  files?: string
  // 扩展/保留字段（如果后端确实有）
  originalFileCode?: string // 如果这是委外特有的，且后端必须传
  supplierName?: string // 如果这是委外特有的
  // 关联信息
  processLibraryIds?: number[]
  processLibraryItemIds?: number[]
  processLibraryName?: string
}

export interface OutsourcedDocumentSaveDTO {
  id?: string
  originalFileName: string // 统一
  fileType: number
  version?: string
  fileStatus?: number
  remark?: string
  files?: string | File
  processLibraryIds?: number[]
  processLibraryItemIds?: number[]
  // 特有字段保留
  originalFileCode?: string
  supplierName?: string
}

export interface OutsourcedDocumentUpdateDTO extends OutsourcedDocumentSaveDTO {
  revisedContent?: string
  changeReason?: string
  changePeople?: string
  changeTime?: string
  libraryOutsourcedFileId?: string
}

export interface OutsourcedDocumentQueryDTO {
  keyword?: string
  fileType?: number
  fileStatus?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: 'asc' | 'desc'
  current?: number
  size?: number
}

// ==========================================
// 测试规范 (Test Specification)
// ==========================================

// 字段结构与 WorkInstructionInfo 保持一致
export interface TestSpecificationInfo {
  id: string
  originalFileName: string // 统一使用 originalFileName (原 specName)
  fileType: number // 统一使用 fileType (原 testStage: 1:入厂检...)
  version: string
  fileStatus: number // 1:草稿 2:已发布 3:已停用
  remark: string
  suffixName: string
  fileName: string
  bucketName: string
  createBy: string
  creator: string
  createTime: string
  updateBy: string
  updateTime: string
  isDeleted: number
  files?: string
  // 特有字段保留 (如果需要)
  fileCode?: string
  applicableSubjects?: string
  // 关联信息
  processLibraryIds?: number[]
  processLibraryItemIds?: number[]
  processLibraryName?: string
}

export interface TestSpecificationSaveDTO {
  id?: string
  originalFileName: string // 对应 specName
  fileType: number // 对应 testStage
  version?: string
  fileStatus?: number
  remark?: string
  files?: string | File
  processLibraryIds?: number[]
  processLibraryItemIds?: number[]
  // 特有
  fileCode?: string
  applicableSubjects?: string
}

export interface TestSpecificationUpdateDTO extends TestSpecificationSaveDTO {
  revisedContent?: string
  changeReason?: string
  changePeople?: string
  changeTime?: string
  libraryTestSpecFileId?: string
}

export interface TestSpecificationQueryDTO {
  keyword?: string
  fileType?: number // 对应 testStage
  fileStatus?: number
  startDate?: string
  endDate?: string
  sortColumn?: string
  sortType?: 'asc' | 'desc'
  current?: number
  size?: number
}

// 扩展 PageResult 泛型
export interface PageResult<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}
