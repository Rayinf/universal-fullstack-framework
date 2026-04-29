import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'

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

// 分页响应
interface PageResponse<T> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

// API响应结构
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
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

export const useDeptStore = defineStore('dept', () => {
  // 状态
  const deptTree = ref<DeptTreeNode[]>([])
  const deptList = ref<SysDept[]>([])
  const currentDept = ref<SysDept | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const userTreeList = ref<UserTreeNode[]>([])  // 扁平用户列表
  const userTreeData = ref<TreeSelectNode[]>([])  // 树形选择器数据
  const userListLoading = ref(false)

  // 将API返回的树形数据转换为前端需要的格式
  // 所有ID字段统一使用string类型，避免大数字精度丢失
  const convertTreeNode = (node: any): DeptTreeNode => {
    // 从 deptInfo 中获取更详细的信息
    const deptInfo = node.deptInfo || {}

    const result: DeptTreeNode = {
      id: String(node.id || deptInfo.deptId || '0'),
      name: node.name || deptInfo.name || '',
      parentId: String(node.parentId || '0'),
      sortOrder: deptInfo.sortOrder ?? node.weight ?? 0,
      enabled: deptInfo.enabled ?? 0,
      level: deptInfo.level,
      tenantCode: deptInfo.tenantCode,
      label: node.name || deptInfo.name || '', // Element Plus tree 使用的label
      userCount: parseInt(deptInfo.userCount) || 0,
      childDeptCount: parseInt(deptInfo.childDeptCount) || 0,
      type: 0, // 部门类型
    }

    // 收集子节点：部门 + 用户
    const childNodes: DeptTreeNode[] = []

    // 1. 添加子部门
    if (node.children && Array.isArray(node.children) && node.children.length > 0) {
      node.children.forEach((child: any) => {
        childNodes.push(convertTreeNode(child))
      })
    }

    // 2. 添加部门下的用户作为子节点
    if (node.userList && Array.isArray(node.userList) && node.userList.length > 0) {
      node.userList.forEach((user: any) => {
        const userNode: DeptTreeNode = {
          id: String(user.userId || '0'),
          name: user.realName || user.username || '',
          parentId: result.id,
          label: user.realName || user.username || '',
          type: 1, // 用户类型
          isLeaf: true,
          // 用户额外信息
          userId: String(user.userId || ''),
          username: user.username,
          realName: user.realName,
          phone: user.phone,
          email: user.email,
        }
        childNodes.push(userNode)
      })
    }

    if (childNodes.length > 0) {
      result.children = childNodes
      result.isLeaf = false
    } else {
      result.isLeaf = true
    }

    return result
  }

  // 获取部门树形菜单（使用 tree 接口）
  const fetchDeptTreeList = async (params?: DeptQueryParams) => {
    loading.value = true
    try {
      // 使用 tree 接口替代 getDeptTreeList
      const response = await request.get<any[]>('/admin/dept/tree')

      if (response.code === 200 && response.data) {
        deptTree.value = response.data.map(convertTreeNode)
        return deptTree.value
      } else {
        ElMessage.error(response.msg || '获取部门树失败')
        deptTree.value = []
        return []
      }
    } catch (error) {
      console.error('获取部门树失败:', error)
      ElMessage.error('获取部门树时发生网络错误')
      deptTree.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  // 获取简单树形菜单
  const fetchDeptTree = async (userId?: number, isAdmin?: number) => {
    loading.value = true
    try {
      const params: Record<string, any> = {}
      if (userId !== undefined) params.userId = userId
      if (isAdmin !== undefined) params.isAdmin = isAdmin

      const response = await request.get<any[]>('/admin/dept/tree', params)

      if (response.code === 200 && response.data) {
        deptTree.value = response.data.map(convertTreeNode)
        return deptTree.value
      } else {
        ElMessage.error(response.msg || '获取部门树失败')
        deptTree.value = []
        return []
      }
    } catch (error) {
      console.error('获取部门树失败:', error)
      ElMessage.error('获取部门树时发生网络错误')
      deptTree.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  // 获取当前用户的部门树
  const fetchUserDeptTree = async (isAdmin?: boolean) => {
    loading.value = true
    try {
      const params: Record<string, any> = {}
      if (isAdmin !== undefined) params.isAdmin = isAdmin

      const response = await request.get<any[]>('/admin/dept/user-tree', params)

      if (response.code === 200 && response.data) {
        deptTree.value = response.data.map(convertTreeNode)
        return deptTree.value
      } else {
        ElMessage.error(response.msg || '获取部门树失败')
        deptTree.value = []
        return []
      }
    } catch (error) {
      console.error('获取部门树失败:', error)
      ElMessage.error('获取部门树时发生网络错误')
      deptTree.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  // 转换用户树节点（扁平列表用）
  // 转换用户节点（支持两种数据格式：顶层用户和 userList 中的用户）
  // 所有 ID 统一使用 string 类型，避免大数字精度丢失
  const convertUserTreeNode = (node: any): UserTreeNode => {
    // userList 中的用户使用 userId, realName, username
    // 顶层用户使用 id, name
    const userId = String(node.userId || node.id || '')
    const realName = node.realName || node.name || ''
    const username = node.username || node.name || ''

    return {
      id: userId,
      name: realName,
      parentId: String(node.parentId || '0'),
      userId: userId,
      username: username,
      realName: realName,
    }
  }

  // 转换为树形选择器节点（使用字符串ID避免大数字精度丢失）
  const convertToTreeSelectNode = (node: any): TreeSelectNode => {
    const nodeType = String(node.type ?? '0')
    const isUser = nodeType === '1'

    // 判断 ID 来源：userList 中的用户使用 userId，其他使用 id
    const nodeId = String(node.userId || node.id || '')

    // 判断名称来源：userList 中的用户使用 realName/username，其他使用 name
    const nodeName = node.realName || node.username || node.name || ''

    const result: TreeSelectNode = {
      id: nodeId,
      label: nodeName,
      value: nodeId,
      type: nodeType,
      disabled: !isUser, // 部门节点不可选，只能选择用户
    }

    // 递归处理子节点
    const childNodes: TreeSelectNode[] = []

    if (node.children && Array.isArray(node.children) && node.children.length > 0) {
      node.children.forEach((child: any) => {
        childNodes.push(convertToTreeSelectNode(child))
      })
    }

    // userList 中的用户也添加为子节点（这些用户没有 type 字段，需要标记为用户）
    if (node.userList && Array.isArray(node.userList) && node.userList.length > 0) {
      node.userList.forEach((user: any) => {
        // userList 中的用户一定是用户类型
        const userNode: TreeSelectNode = {
          id: String(user.userId || ''),
          label: user.realName || user.username || '',
          value: String(user.userId || ''),
          type: '1', // 用户类型
          disabled: false, // 可选
        }
        childNodes.push(userNode)
      })
    }

    if (childNodes.length > 0) {
      result.children = childNodes
    }

    return result
  }

  // 获取用户树列表（用于选择部门成员）
  const fetchUserTreeForSelect = async () => {
    userListLoading.value = true
    try {
      // 使用 /admin/dept/tree 接口，不传参数
      const response = await request.get<any[]>('/admin/dept/tree')

      if (response.code === 200 && response.data) {
        // 1. 保存树形结构（用于树形选择器）
        userTreeData.value = response.data.map(convertToTreeSelectNode)

        // 2. 扁平化用户列表（用于回显等）
        const flattenUsers: UserTreeNode[] = []
        const flatten = (nodes: any[]) => {
          nodes.forEach((node) => {
            const nodeType = String(node.type)
            if (nodeType === '1') {
              flattenUsers.push(convertUserTreeNode(node))
            }
            if (node.children && Array.isArray(node.children)) {
              flatten(node.children)
            }
            if (node.userList && Array.isArray(node.userList) && node.userList.length > 0) {
              node.userList.forEach((user: any) => {
                flattenUsers.push(convertUserTreeNode(user))
              })
            }
          })
        }
        flatten(response.data)
        userTreeList.value = flattenUsers

        return userTreeData.value
      } else {
        userTreeList.value = []
        userTreeData.value = []
        return []
      }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      userTreeList.value = []
      userTreeData.value = []
      return []
    } finally {
      userListLoading.value = false
    }
  }

  // 分页查询部门
  const fetchDeptPage = async (pageParams: DeptPageParams, queryParams?: DeptQueryParams) => {
    loading.value = true
    try {
      const params = {
        page: {
          current: pageParams.current,
          size: pageParams.size,
        },
        dto: {
          sortColumn: 'sort_order',
          sortType: 'asc',
          ...queryParams,
        },
      }

      const response = await request.get<PageResponse<SysDept>>('/admin/dept/page', params)

      if (response.code === 200 && response.data) {
        // 将ID字段转换为string类型
        deptList.value = (response.data.records || []).map(dept => ({
          ...dept,
          deptId: String(dept.deptId || ''),
          parentId: String(dept.parentId || '0'),
          parentPath: dept.parentPath ? String(dept.parentPath) : undefined,
        }))
        total.value = response.data.total || 0
        return response.data
      } else {
        ElMessage.error(response.msg || '获取部门列表失败')
        deptList.value = []
        total.value = 0
        return null
      }
    } catch (error) {
      console.error('获取部门列表失败:', error)
      ElMessage.error('获取部门列表时发生网络错误')
      deptList.value = []
      total.value = 0
      return null
    } finally {
      loading.value = false
    }
  }

  // 通过ID查询部门详情
  // 确保返回的ID字段为string类型，避免大数字精度丢失
  const fetchDeptById = async (id: string) => {
    loading.value = true
    try {
      const response = await request.get<SysDept>(`/admin/dept/${id}`)

      if (response.code === 200 && response.data) {
        // 将ID字段转换为string类型
        const deptData: SysDept = {
          ...response.data,
          deptId: String(response.data.deptId || ''),
          parentId: String(response.data.parentId || '0'),
          parentPath: response.data.parentPath ? String(response.data.parentPath) : undefined,
        }
        currentDept.value = deptData
        return deptData
      } else {
        ElMessage.error(response.msg || '获取部门详情失败')
        currentDept.value = null
        return null
      }
    } catch (error) {
      console.error('获取部门详情失败:', error)
      ElMessage.error('获取部门详情时发生网络错误')
      currentDept.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  // 根据部门名称查询部门信息
  // 确保返回的ID字段为string类型
  const fetchDeptByName = async (deptName: string) => {
    loading.value = true
    try {
      const response = await request.get<SysDept>(`/admin/dept/details/${encodeURIComponent(deptName)}`)

      if (response.code === 200 && response.data) {
        // 将ID字段转换为string类型
        const deptData: SysDept = {
          ...response.data,
          deptId: String(response.data.deptId || ''),
          parentId: String(response.data.parentId || '0'),
          parentPath: response.data.parentPath ? String(response.data.parentPath) : undefined,
        }
        return deptData
      } else {
        ElMessage.error(response.msg || '获取部门信息失败')
        return null
      }
    } catch (error) {
      console.error('获取部门信息失败:', error)
      ElMessage.error('获取部门信息时发生网络错误')
      return null
    } finally {
      loading.value = false
    }
  }

  // 添加部门
  const addDept = async (deptData: Partial<SysDept>, userIdList?: string[]) => {
    loading.value = true
    try {
      // 统一使用 string 类型的 ID
      const requestBody: DeptSaveRequest = {
        sysDept: deptData,
        userIdList: userIdList || [],
      }

      const response = await request.post<any>('/admin/dept', requestBody)

      if (response.code === 200) {
        ElMessage.success('部门添加成功')
        // 刷新部门树
        await fetchDeptTree()
        return true
      } else {
        ElMessage.error(response.msg || '部门添加失败')
        return false
      }
    } catch (error) {
      console.error('部门添加失败:', error)
      ElMessage.error('部门添加时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 编辑部门
  const updateDept = async (deptData: Partial<SysDept>, userIdList?: string[]) => {
    loading.value = true
    try {
      // 统一使用 string 类型的 ID
      const requestBody: DeptSaveRequest = {
        sysDept: deptData,
        userIdList: userIdList || [],
      }

      const response = await request.put<any>('/admin/dept', requestBody)

      if (response.code === 200) {
        ElMessage.success('部门更新成功')
        // 刷新部门树
        await fetchDeptTree()
        return true
      } else {
        ElMessage.error(response.msg || '部门更新失败')
        return false
      }
    } catch (error) {
      console.error('部门更新失败:', error)
      ElMessage.error('部门更新时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 删除部门
  const deleteDept = async (id: string) => {
    loading.value = true
    try {
      const response = await request.delete<any>(`/admin/dept/${id}`)

      if (response.code === 200) {
        ElMessage.success('部门删除成功')
        // 刷新部门树
        await fetchDeptTree()
        return true
      } else {
        ElMessage.error(response.msg || '部门删除失败')
        return false
      }
    } catch (error) {
      console.error('部门删除失败:', error)
      ElMessage.error('部门删除时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 启用/停用部门
  const toggleDeptEnabled = async (id: string, type: 0 | 1) => {
    loading.value = true
    try {
      const response = await request.get<any>('/admin/dept/enabled', { id, type })

      if (response.code === 200) {
        ElMessage.success(type === 0 ? '部门已启用' : '部门已停用')
        // 刷新部门树
        await fetchDeptTree()
        return true
      } else {
        ElMessage.error(response.msg || '操作失败')
        return false
      }
    } catch (error) {
      console.error('操作失败:', error)
      ElMessage.error('操作时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 更新部门用户
  const updateDeptUsers = async (deptId: string, userIdList: string[]) => {
    loading.value = true
    try {
      const requestBody: UpdateUserDeptRequest = {
        deptId,
        userIdList,
      }

      const response = await request.post<any>('/admin/dept/updateUserDeptId', requestBody)

      if (response.code === 200) {
        ElMessage.success('部门用户更新成功')
        return true
      } else {
        ElMessage.error(response.msg || '部门用户更新失败')
        return false
      }
    } catch (error) {
      console.error('部门用户更新失败:', error)
      ElMessage.error('部门用户更新时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  // 计算属性：扁平化的部门列表（用于下拉选择）
  const flatDeptList = computed(() => {
    const result: { id: string; name: string; parentId: string; level: number }[] = []

    const flatten = (nodes: DeptTreeNode[], level: number = 0) => {
      nodes.forEach((node) => {
        result.push({
          id: node.id,
          name: node.name,
          parentId: node.parentId,
          level,
        })
        if (node.children && node.children.length > 0) {
          flatten(node.children, level + 1)
        }
      })
    }

    flatten(deptTree.value)
    return result
  })

  // 根据ID获取部门名称
  const getDeptNameById = (id: string): string => {
    const dept = flatDeptList.value.find((d) => d.id === id)
    return dept ? dept.name : ''
  }

  // 检查是否可以删除部门（无子部门且无用户）
  const canDeleteDept = (dept: SysDept | DeptTreeNode): boolean => {
    const childCount = 'childDeptCount' in dept ? dept.childDeptCount || 0 : 0
    const userCount = 'userCount' in dept ? dept.userCount || 0 : 0
    const hasChildren = 'children' in dept && dept.children && dept.children.length > 0
    return childCount === 0 && userCount === 0 && !hasChildren
  }

  return {
    // 状态
    deptTree,
    deptList,
    currentDept,
    loading,
    total,
    userTreeList,
    userTreeData,
    userListLoading,

    // 计算属性
    flatDeptList,

    // 方法
    fetchDeptTreeList,
    fetchDeptTree,
    fetchUserDeptTree,
    fetchUserTreeForSelect,
    fetchDeptPage,
    fetchDeptById,
    fetchDeptByName,
    addDept,
    updateDept,
    deleteDept,
    toggleDeptEnabled,
    updateDeptUsers,
    getDeptNameById,
    canDeleteDept,
  }
})
