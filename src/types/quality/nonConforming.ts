// 发现时机枚举
export enum DiscoveryTiming {
  INCOMING = 1, // 进货检验
  SEMI_PRODUCT = 2, // 半成品检验
  PROCESS = 3, // 研制过程检验
  FINAL = 4, // 最终检验或试验
}

// 严重程度枚举
export enum Severity {
  SERIOUS = 1, // 严重
  GENERAL = 2, // 一般
  SLIGHT = 3, // 轻度
}

// 评审人员类型枚举
export enum ReviewType {
  TEAM = 1, // 小组
  OFFICE = 2, // 办公室
  COMMITTEE = 3, // 委员会
}

// 评审状态枚举
export enum ReviewStatus {
  PENDING = 1, // 待评审
  PASSED = 2, // 评审通过
  REJECTED = 3, // 评审不通过
  COMPLETED = 3, // 评审完成 (Note: The interface doc says 3 is 'Completed' in updateReview, but 'Rejected' in getReviewById. Assuming context based usage, but standardizing on Completed for flow)
}

// 评审记录 VO
export interface ReviewRecord {
  id: string
  reportId: string
  status: number // 1:待评审 2:评审通过 3:评审不通过
  reviewOpinion: string // 不合格品审理意见
  reviewUserId: string // 不合格品审理人员id
  reviewType: number // 1：小组 2：办公室 3：委员会
  reviewDate: string // 审理确认日期
  createBy: number
  createTime: string
  updateBy: number
  updateTime: string
}

// 返工记录 VO
export interface ReworkRecord {
  id: string
  reportId: string
  customerRepresentativeOpinion: string // 顾客代表意见
  customerRepresentative: string // 顾客代表签字
  customerRepresentativeDate: string // 顾客代表签字日期
  reworkRecheckResult: string // 返工、返修复检结果
  inspector: string // 检验员
  recheckDate: string // 复检日期
}

// 不合格品主记录
export interface NonConformingReport {
  id: string
  reportNo: string // 编号
  serialNo: string // 序号
  model: string // 型号
  productionPhase: string // 生产阶段
  productName: string // 产品(或零部件)名称
  productNo: string // 产品编号
  matchingObject: string // 配套对象
  productDrawingNo: string // 产品图(代)号
  processNo: string // 工序号
  inspectedQuantity: number // 送检数
  unqualifiedProductNo: string // 不合格品编号
  responsibleDepartment: string // 责任部门名称
  responsibleDepartmentId?: string // 责任部门ID
  operator: string // 操作者
  unqualifiedQuantity: number // 不合格品数量
  discoveryTiming: number // 发现不合格时机
  unqualifiedType: number // 不合格类型
  unqualifiedDescription: string // 不合格品情况事实描述
  inspector: string // 检验员
  inspectDate: string // 检验日期

  // 责任部门填报
  causeAnalysisAndMeasures?: string // 原因分析和拟采取的纠正措施
  responsibleDeptConfirm?: string // 责任部门确认签字
  confirmDate?: string // 责任部门确认日期

  isVoided: number // 是否作废:1-是,0-否
  createBy: number
  creator?: string
  createTime?: string
  unquTime?: string // 创建时间 (API Schema)
  updateBy: number
  updateTime?: string
}

// 详情接口完整响应结构
export interface NonConformingDetailRes {
  unqualifiedProductReportVO: NonConformingReport
  unqualifiedProductReviewVOS: ReviewRecord[]
  unqualifiedProductReworkVOS: ReworkRecord[]
}

// 分页查询参数
export interface NonConformingQueryDTO {
  page: {
    current: number
    size: number
  }
  dto: {
    reportNo?: string
    productName?: string
    unqualifiedType?: number
    discoveryTiming?: number
    // status? 接口文档DTO里没写状态筛选，但通常会有
  }
}

// 评审意见保存 DTO
export interface ReviewSaveDTO {
  id?: string
  reportId: string
  status: number // 1：待评审 3：评审完成
  reviewOpinion: string
  reviewUserId: string
  reviewType: number // 1：小组 2：办公室 3：委员会
  reviewTeamDate: string
}
