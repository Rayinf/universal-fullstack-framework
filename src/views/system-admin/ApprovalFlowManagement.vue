<template>
  <div class="page-view">
    <!-- 统一页面头部 -->
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>业务相关审批规则</h2>
          <div class="page-description">
            定义业务事项（如工艺库、排程、采购订单、报价单、生产工单）的电子化审批流程节点与人员。
          </div>
        </div>
      </div>
    </div>

    <!-- 页面内容卡片 -->
    <div class="content-card">
      <!-- 搜索操作面板 -->
      <div class="search-actions-panel">
        <el-form :model="query" inline class="filter-form" @submit.prevent>
          <el-form-item label="规则名称">
            <el-input
              v-model="query.keyword"
              placeholder="请输入规则名称"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="审批类型">
            <el-select
              v-model="query.approvalType"
              placeholder="全部类型"
              clearable
              style="width: 150px"
            >
              <el-option label="工艺库" :value="1" />
              <el-option label="排程" :value="2" />
              <el-option label="采购订单" :value="3" />
              <el-option label="报价单" :value="4" />
              <el-option label="生产工单" :value="5" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 120px">
              <el-option label="启用" :value="1" />
              <el-option label="未启用" :value="2" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>重置
            </el-button>
          </el-form-item>
        </el-form>
        <div class="actions">
          <el-button type="primary" :icon="Plus" @click="handleCreate"> 新增规则 </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-container">
        <el-table
          v-loading="loading"
          :data="tableData"
          stripe
          highlight-current-row
          class="unified-table"
        >
          <el-table-column
            prop="approvalFlowName"
            label="规则名称"
            min-width="180"
            show-overflow-tooltip
          />
          <el-table-column prop="approvalType" label="审批类型" width="120">
            <template #default="{ row }">
              <el-tag :type="approvalTypeTagType(row.approvalType)" effect="plain">
                {{ approvalTypeText(row.approvalType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="processLibraryName" label="关联工艺库" min-width="150">
            <template #default="{ row }">
              {{
                row.approvalType === 1
                  ? row.processLibraryName || getProcessLibraryName(row.processLibraryId)
                  : '-'
              }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="dark">
                {{ row.status === 1 ? '启用' : '未启用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="creator" label="创建人" width="120" />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column label="操作" width="280" fixed="right" align="center">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">
                  编辑
                </el-button>
                <el-button type="primary" link :icon="Setting" @click="handleConfigNodes(row)">
                  配置节点
                </el-button>
                <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 规则新增/编辑弹窗 -->
    <FormDialog
      v-model="formVisible"
      :title="isEdit ? '编辑审批规则' : '新增审批规则'"
      :form-data="formData"
      :rules="formRules"
      :loading="submitLoading"
      width="550px"
      @submit="handleFormSubmit"
    >
      <template #default="{ formData }">
        <el-form-item label="规则名称" prop="approvalFlowName">
          <el-input v-model="formData.approvalFlowName" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="审批类型" prop="approvalType">
          <el-select
            v-model="formData.approvalType"
            placeholder="请选择审批类型"
            class="w-full"
            @change="handleApprovalTypeChange"
          >
            <el-option label="工艺库" :value="1" />
            <el-option label="排程" :value="2" />
            <el-option label="采购订单" :value="3" />
            <el-option label="报价单" :value="4" />
            <el-option label="生产工单" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.approvalType === 1" label="关联工艺库" prop="processLibraryId">
          <el-select
            v-model="formData.processLibraryId"
            placeholder="请选择工艺库"
            filterable
            class="w-full"
          >
            <el-option
              v-for="item in processLibraryOptions"
              :key="item.id"
              :label="item.processName"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="2">未启用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </template>
    </FormDialog>

    <!-- 审批节点配置弹窗 -->
    <el-dialog
      v-model="nodeConfigVisible"
      :title="currentFlow ? `配置审批节点 - ${currentFlow.approvalFlowName}` : '配置审批节点'"
      width="800px"
      destroy-on-close
    >
      <div class="node-config-container" v-loading="nodesLoading">
        <div class="node-actions">
          <el-button type="primary" :icon="Plus" size="small" @click="handleAddNode"
            >添加节点</el-button
          >
          <span class="node-tip">提示：节点将按下方列表顺序依次进行审批。</span>
        </div>

        <el-table :data="nodeList" border style="margin-top: 15px">
          <el-table-column label="顺序" width="70" align="center">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column label="节点名称" min-width="150">
            <template #default="{ row }">
              <el-input
                v-model="row.approvalNodeName"
                placeholder="如：部门经理审核"
                size="small"
              />
            </template>
          </el-table-column>
          <el-table-column label="配置审批人" min-width="350">
            <template #default="{ row }">
              <div class="assign-config">
                <el-row :gutter="10">
                  <el-col :span="10">
                    <el-select
                      v-model="row.roleId"
                      placeholder="指定角色"
                      size="small"
                      class="w-full"
                      filterable
                      clearable
                      @change="handleRoleChange(row)"
                    >
                      <el-option
                        v-for="role in roleOptions"
                        :key="role.roleId"
                        :label="role.roleName"
                        :value="role.roleId"
                      />
                    </el-select>
                  </el-col>
                  <el-col :span="14">
                    <el-select
                      v-model="row.userList"
                      :placeholder="row.roleId ? '指定具体用户' : '请先选择角色'"
                      size="small"
                      class="w-full"
                      multiple
                      collapse-tags
                      collapse-tags-tooltip
                      filterable
                      clearable
                      :disabled="!row.roleId"
                    >
                      <el-option
                        v-for="user in getFilteredUsers(row)"
                        :key="user.userId"
                        :label="user.realName || user.username"
                        :value="user.userId.toString()"
                      />
                    </el-select>
                  </el-col>
                </el-row>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button link type="danger" @click="handleRemoveNode($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="nodeConfigVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSaveNodes"
          >保存配置</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Plus, Edit, Delete, Setting } from '@element-plus/icons-vue'
import type {
  ApprovalFlow,
  ApprovalFlowPageQuery,
  ApprovalFlowSaveDTO,
  ApprovalFlowUpdateDTO,
  ApprovalFlowNodeSaveDTO,
} from '@/types/approvalFlow'
import type { Role, UserRecord } from '@/types/system/user'
import type { ProcessLibrary } from '@/types/technology'
import {
  pageApprovalFlowApi,
  saveApprovalFlowApi,
  updateApprovalFlowApi,
  deleteApprovalFlowApi,
  getApprovalFlowDetailApi,
  saveApprovalFlowNodesApi,
} from '@/api/approvalFlow'
import { getAllUsersApi } from '@/api/system/user'
import { getUsersByRoleIdApi } from '@/api/system/role'
import request from '@/utils/request'
import FormDialog from '@/components/common/FormDialog.vue'

// --- 状态变量 ---
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<ApprovalFlow[]>([])
const query = reactive<ApprovalFlowPageQuery>({
  keyword: '',
  approvalType: undefined,
  status: undefined,
})
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0,
})

// 表单相关
const formVisible = ref(false)
const isEdit = ref(false)
const formData = reactive<ApprovalFlowSaveDTO & { id?: number }>({
  approvalFlowName: '',
  approvalType: 1,
  processLibraryId: undefined,
  status: 1,
  remarks: '',
})
const formRules = {
  approvalFlowName: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  approvalType: [{ required: true, message: '请选择审批类型', trigger: 'change' }],
  processLibraryId: [{ required: true, message: '请选择工艺库', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

// 选项数据
const processLibraryOptions = ref<ProcessLibrary[]>([])
const roleOptions = ref<Role[]>([])
const userOptions = ref<UserRecord[]>([])

// 节点配置相关
const nodeConfigVisible = ref(false)
const nodesLoading = ref(false)
const currentFlow = ref<ApprovalFlow | null>(null)
const nodeList = ref<any[]>([])

// 每个角色对应的用户列表缓存
const roleUsersMap = ref<Map<string, string[]>>(new Map())

// --- 方法 ---

// 获取节点可选的用户列表（根据角色过滤）
const getFilteredUsers = (node: any) => {
  if (!node.roleId) {
    return []
  }
  const roleUserIds = roleUsersMap.value.get(String(node.roleId)) || []
  return userOptions.value.filter((user) => roleUserIds.includes(String(user.userId)))
}

// 加载工艺库选项
const loadProcessLibraries = async () => {
  try {
    const res = await request.get<any>('/manage/api/processLibrary/list')
    if (res.code === 0 || res.code === 200) {
      processLibraryOptions.value = res.data || []
    }
  } catch (error) {
    console.error('加载工艺库失败:', error)
  }
}

// 加载角色选项
const loadRoles = async () => {
  try {
    const res = await request.get<any>('/admin/role/list')
    if (res.code === 0 || res.code === 200) {
      roleOptions.value = res.data || []
    }
  } catch (error) {
    console.error('加载角色失败:', error)
  }
}

// 加载用户选项
const loadUsers = async () => {
  try {
    const res = await getAllUsersApi()
    if (res.code === 0 || res.code === 200) {
      userOptions.value = (res.data?.data || res.data || []) as UserRecord[]
    }
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

// 加载表格数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await pageApprovalFlowApi({
      ...query,
      current: pagination.current,
      size: pagination.size,
      sortColumn: 'create_time',
      sortType: 'desc',
    })
    if (res.code === 0 || res.code === 200) {
      tableData.value = (res.data as any).records || []
      pagination.total = (res.data as any).total || 0
    }
  } catch (error) {
    console.error('获取审批规则失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  query.keyword = ''
  query.approvalType = undefined
  query.status = undefined
  handleSearch()
}

const handleSizeChange = (val: number) => {
  pagination.size = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  pagination.current = val
  loadData()
}

// 新增/编辑
const handleCreate = () => {
  isEdit.value = false
  Object.assign(formData, {
    id: undefined,
    approvalFlowName: '',
    approvalType: 1,
    processLibraryId: undefined,
    status: 1,
    remarks: '',
  })
  formVisible.value = true
}

const handleEdit = (row: ApprovalFlow) => {
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    approvalFlowName: row.approvalFlowName,
    approvalType: row.approvalType,
    processLibraryId: row.processLibraryId,
    status: row.status,
    remarks: row.remarks,
  })
  formVisible.value = true
}

const handleApprovalTypeChange = (val: 1 | 2 | 3 | 4 | 5) => {
  if (val !== 1) {
    formData.processLibraryId = undefined
  }
}

const approvalTypeText = (approvalType: number) => {
  if (approvalType === 1) return '工艺库'
  if (approvalType === 2) return '排程'
  if (approvalType === 3) return '采购订单'
  if (approvalType === 4) return '报价单'
  if (approvalType === 5) return '生产工单'
  return '未知类型'
}

const approvalTypeTagType = (
  approvalType: number,
): 'primary' | 'success' | 'warning' | 'danger' => {
  if (approvalType === 1) return 'primary'
  if (approvalType === 2) return 'success'
  if (approvalType === 4) return 'danger'
  if (approvalType === 5) return 'warning'
  return 'warning'
}

const handleFormSubmit = async () => {
  submitLoading.value = true
  try {
    const submitData = { ...formData }
    if (submitData.approvalType !== 1) {
      delete submitData.processLibraryId
    }

    let res
    if (isEdit.value && submitData.id) {
      res = await updateApprovalFlowApi(submitData as ApprovalFlowUpdateDTO)
    } else {
      res = await saveApprovalFlowApi(submitData as ApprovalFlowSaveDTO)
    }

    if (res.code === 0 || res.code === 200) {
      ElMessage.success('保存成功')
      formVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('提交表单失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row: ApprovalFlow) => {
  ElMessageBox.confirm(`确定要删除审批规则 "${row.approvalFlowName}" 吗？`, '提示', {
    type: 'warning',
  }).then(async () => {
    try {
      const res = await deleteApprovalFlowApi(row.id!)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

// 节点配置
const handleConfigNodes = async (row: ApprovalFlow) => {
  currentFlow.value = row
  nodeConfigVisible.value = true
  nodesLoading.value = true
  nodeList.value = []
  // 清空角色用户缓存
  roleUsersMap.value.clear()

  try {
    const res = await getApprovalFlowDetailApi(row.id!)
    if (res.code === 0 || res.code === 200) {
      const details = (res.data as any) || []
      nodeList.value = details.map((d: any) => ({
        id: d.id,
        approvalNodeName: d.approvalNodeName,
        roleId: d.roleId,
        userList: d.approvalIds ? d.approvalIds.split(',') : [],
        remarks: d.remarks,
      }))

      // 预加载所有节点角色的用户列表
      const roleIds = [...new Set(nodeList.value.map((n) => n.roleId).filter(Boolean))]
      await Promise.all(
        roleIds.map(async (roleId) => {
          try {
            const userRes = await getUsersByRoleIdApi(roleId)
            if (userRes.code === 0 || userRes.code === 200) {
              const userIds = (userRes.data || []).map((id: number) => String(id))
              roleUsersMap.value.set(String(roleId), userIds)
            }
          } catch (error) {
            console.error(`加载角色 ${roleId} 的用户失败:`, error)
          }
        }),
      )

      if (nodeList.value.length === 0) {
        handleAddNode()
      }
    }
  } catch (error) {
    console.error('获取节点详情失败:', error)
  } finally {
    nodesLoading.value = false
  }
}

const handleAddNode = () => {
  nodeList.value.push({
    approvalNodeName: '',
    roleId: undefined,
    userList: [],
    remarks: '',
  })
}

const handleRemoveNode = (index: number) => {
  nodeList.value.splice(index, 1)
}

const getProcessLibraryName = (id?: string | number) => {
  if (id === undefined || id === null || id === '') return '-'
  const found = processLibraryOptions.value.find((item) => String(item.id) === String(id))
  return found ? found.processName : '-'
}

const handleSaveNodes = async () => {
  if (!currentFlow.value) return

  for (let i = 0; i < nodeList.value.length; i++) {
    const node = nodeList.value[i]
    if (!node.approvalNodeName) {
      ElMessage.warning(`第 ${i + 1} 个节点的名称不能为空`)
      return
    }
    if (!node.roleId && (!node.userList || node.userList.length === 0)) {
      ElMessage.warning(`第 ${i + 1} 个节点必须指定角色或具体用户`)
      return
    }
  }

  submitLoading.value = true
  try {
    const payload: ApprovalFlowNodeSaveDTO[] = nodeList.value.map((n, index) => ({
      approvalFlowId: currentFlow.value!.id!,
      approvalNodeName: n.approvalNodeName,
      nodeIndex: index + 1,
      roleId: n.roleId,
      approvalIds: n.userList && n.userList.length > 0 ? n.userList.join(',') : undefined,
      remarks: n.remarks,
    }))

    const res = await saveApprovalFlowNodesApi(payload)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('节点配置保存成功')
      nodeConfigVisible.value = false
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存节点失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 角色选择联动 - 加载该角色下的用户列表
const handleRoleChange = async (node: any) => {
  // 清空用户选择
  node.userList = []

  if (!node.roleId) {
    return
  }

  // 检查缓存
  if (roleUsersMap.value.has(String(node.roleId))) {
    return
  }

  try {
    const res = await getUsersByRoleIdApi(node.roleId)
    if (res.code === 0 || res.code === 200) {
      const userIds = (res.data || []).map((id: number) => String(id))
      roleUsersMap.value.set(String(node.roleId), userIds)
      ElMessage.success(`该角色下有 ${userIds.length} 位可选用户`)
    } else {
      ElMessage.warning('获取角色用户失败: ' + (res.msg || '未知错误'))
    }
  } catch (error) {
    console.error('获取角色用户失败:', error)
    ElMessage.error('获取角色用户时发生错误')
  }
}

onMounted(() => {
  loadData()
  loadProcessLibraries()
  loadRoles()
  loadUsers()
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.table-container {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.unified-table {
  width: 100%;
  max-height: calc(100vh - 380px);
  overflow-y: auto;
}

.node-config-container {
  min-height: 200px;
}

.node-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.node-tip {
  font-size: 12px;
  color: #909399;
}

.assign-type {
  display: flex;
  flex-direction: column;
}

.w-full {
  width: 100%;
}

.table-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
