// 导出所有 store 模块
export { useDeptStore } from './modules/dept'
export { useSystemConfigStore } from './modules/systemConfig'

// 导出类型定义
export type { 
  SysDept, 
  DeptTreeNode, 
  DeptUser,
  DeptSaveRequest,
  UpdateUserDeptRequest,
  DeptQueryParams,
  DeptPageParams,
  UserTreeNode,
  TreeSelectNode
} from '../types/dept'

export type { 
  SystemConfigData, 
  UpdateConfigRequest,
  ConfigCode
} from '../types/systemConfig'