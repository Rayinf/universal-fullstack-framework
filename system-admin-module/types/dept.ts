// 部门用户信息（所有ID使用string类型避免大数字精度丢失）
export interface DeptUser {
  userId: string
  username: string
  realName: string
  phone?: string
  email?: string
  deptId?: string
  enabled: 0 | 1
  tenantCode?: string
  region?: string
}

// 部门信息接口
export interface SysDept {
  deptId: string
  name: string
  sortOrder: number
  parentId: string
  parentName?: string
  delFlag?: string
  level?: string
  parentPath?: string
  enabled: 0 | 1
  tenantCode?: string
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  // 详情接口返回的额外字段
  userCount?: number
  childDeptCount?: number
  totalSize?: number
  totalSizeStr?: string
  usedSize?: number
  usedSizeStr?: string
  userList?: DeptUser[]
  creator?: string
}

// 树形节点接口
export interface DeptTreeNode {
  id: string
  name: string
  parentId: string
  sortOrder?: number
  enabled?: 0 | 1
  level?: string
  tenantCode?: string
  children?: DeptTreeNode[]
  userCount?: number
  childDeptCount?: number
  // Element Plus tree 组件需要的字段
  label?: string
  isLeaf?: boolean
  // 节点类型：0-部门，1-用户
  type?: 0 | 1
  // 用户信息（当 type=1 时有效）
  userId?: string
  username?: string
  realName?: string
  phone?: string
  email?: string
}

// 保存/更新部门请求体
export interface DeptSaveRequest {
  sysDept: Partial<SysDept>
  userIdList?: string[]
}

// 更新部门用户请求体
export interface UpdateUserDeptRequest {
  deptId: string
  userIdList: string[]
}

// 查询参数
export interface DeptQueryParams {
  sortColumn?: string
  sortType?: string
  name?: string
  parentId?: string
  startTime?: string
  endTime?: string
  tenantCode?: string
}

// 分页查询参数
export interface DeptPageParams extends DeptQueryParams {
  current: number
  size: number
}

// 用户树节点（用于选择用户）
export interface UserTreeNode {
  id: string
  name: string
  parentId: string
  userId?: string
  username?: string
  realName?: string
  children?: UserTreeNode[]
}

// 树形选择器节点（使用字符串ID避免大数字精度丢失）
export interface TreeSelectNode {
  id: string
  label: string
  value: string
  type: string  // '0' 部门, '1' 用户
  disabled?: boolean
  children?: TreeSelectNode[]
}
