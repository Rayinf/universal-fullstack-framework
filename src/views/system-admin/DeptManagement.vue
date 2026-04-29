<template>
  <div class="dept-management-view page-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>组织架构管理</h2>
          <div class="page-description">
            管理公司的组织架构体系，包括创建、编辑、删除组织，以及管理组织层级关系
          </div>
        </div>
      </div>
    </div>

    <!-- 内容卡片 -->
    <div class="content-card">
      <div class="dept-layout">
        <!-- 左侧树形结构 -->
        <div class="tree-panel">
          <div class="tree-header">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索组织或成员"
              clearable
              class="search-input"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button
              type="primary"
              @click="handleAddRootDept"
              :icon="Plus"
              circle
              size="small"
              title="添加顶级组织"
            />
          </div>

          <div class="tree-content" v-loading="deptStore.loading">
            <el-tree
              ref="treeRef"
              :data="deptStore.deptTree"
              :props="{ label: 'name', children: 'children' }"
              node-key="id"
              :expand-on-click-node="false"
              :filter-node-method="filterNode"
              class="dept-tree"
              @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <div class="node-content">
                    <el-icon class="node-icon" :class="{ 'is-user': data.type === 1 }">
                      <OfficeBuilding v-if="data.type === 0" />
                      <User v-else />
                    </el-icon>
                    <span class="node-label">{{ node.label }}</span>
                    <span v-if="data.type === 0" class="node-count">
                      ({{ data.userCount || 0 }}人)
                    </span>
                  </div>
                  <div v-if="data.type === 0" class="node-actions">
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      circle
                      @click.stop="handleAddChildDept(data)"
                      title="添加子组织"
                    />
                    <el-button
                      type="warning"
                      :icon="Edit"
                      size="small"
                      circle
                      @click.stop="handleEditDept(data)"
                      title="编辑组织"
                    />
                    <el-button
                      type="danger"
                      :icon="Delete"
                      size="small"
                      circle
                      @click.stop="handleDeleteDept(data)"
                      title="删除组织"
                      :disabled="!deptStore.canDeleteDept(data)"
                    />
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </div>

        <!-- 右侧详情面板 -->
        <div class="detail-panel">
          <div v-if="selectedDept" class="dept-detail">
            <div class="detail-header">
              <h3>{{ selectedDept.name }}</h3>
              <div class="detail-actions">
                <el-button type="primary" @click="handleEditDept(selectedDept)" :icon="Edit"
                  >编辑组织</el-button
                >
                <el-button
                  type="danger"
                  @click="handleDeleteDept(selectedDept)"
                  :icon="Delete"
                  :disabled="!deptStore.canDeleteDept(selectedDept)"
                  >删除组织</el-button
                >
              </div>
            </div>

            <div class="detail-content">
              <div class="info-section">
                <h4>基本信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <label>名称：</label>
                    <span>{{ selectedDept.name }}</span>
                  </div>
                  <div class="info-item">
                    <label>上级组织：</label>
                    <span>{{ selectedDept.parentName || '无' }}</span>
                  </div>
                  <div class="info-item">
                    <label>排序：</label>
                    <span>{{ selectedDept.sortOrder }}</span>
                  </div>
                  <div class="info-item">
                    <label>状态：</label>
                    <el-tag :type="selectedDept.enabled === 0 ? 'success' : 'danger'">
                      {{ selectedDept.enabled === 0 ? '启用' : '禁用' }}
                    </el-tag>
                  </div>
                  <div class="info-item">
                    <label>成员数量：</label>
                    <span>{{ selectedDept.userCount || 0 }} 人</span>
                  </div>
                  <div class="info-item">
                    <label>子组织数量：</label>
                    <span>{{ selectedDept.childDeptCount || 0 }} 个</span>
                  </div>
                </div>
              </div>

              <div
                v-if="selectedDept.userList && selectedDept.userList.length > 0"
                class="members-section"
              >
                <h4>成员</h4>
                <div class="members-list">
                  <div
                    v-for="user in selectedDept.userList"
                    :key="user.userId"
                    class="member-item"
                    @click="handleUserClick(user)"
                  >
                    <div class="member-avatar">
                      <el-icon>
                        <User />
                      </el-icon>
                    </div>
                    <div class="member-info">
                      <div class="member-name">{{ user.realName || user.username }}</div>
                      <div class="member-details">
                        <span v-if="user.phone">{{ user.phone }}</span>
                        <span v-if="user.email">{{ user.email }}</span>
                      </div>
                    </div>
                    <div class="member-status">
                      <el-tag :type="user.enabled === 0 ? 'success' : 'danger'" size="small">
                        {{ user.enabled === 0 ? '启用' : '禁用' }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="selectedUser" class="user-detail">
            <div class="detail-header">
              <h3>{{ selectedUser.realName || selectedUser.username }}</h3>
            </div>
            <div class="detail-content">
              <div class="info-section">
                <h4>用户信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <label>用户名：</label>
                    <span>{{ selectedUser.username }}</span>
                  </div>
                  <div class="info-item">
                    <label>真实姓名：</label>
                    <span>{{ selectedUser.realName }}</span>
                  </div>
                  <div class="info-item">
                    <label>电话：</label>
                    <span>{{ selectedUser.phone || '未设置' }}</span>
                  </div>
                  <div class="info-item">
                    <label>邮箱：</label>
                    <span>{{ selectedUser.email || '未设置' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-detail">
            <el-empty description="请选择组织或成员查看详情" />
          </div>
        </div>
      </div>
    </div>

    <!-- 部门表单对话框 -->
    <el-dialog
      v-model="deptDialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
      @close="handleDialogClose"
    >
      <el-form ref="deptFormRef" :model="deptForm" :rules="deptFormRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="deptForm.name"
            placeholder="请输入名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="上级组织" prop="parentId">
          <el-tree-select
            v-model="deptForm.parentId"
            :data="parentTreeOptions"
            :props="{ label: 'name', value: 'id' }"
            placeholder="请选择上级组织（不选则为顶级组织）"
            clearable
            check-strictly
            :render-after-expand="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number
            v-model="deptForm.sortOrder"
            :min="0"
            :max="9999"
            placeholder="数字越小越靠前"
          />
        </el-form-item>
        <el-form-item label="成员">
          <el-tree-select
            v-model="deptForm.userIdList"
            :data="deptStore.userTreeData"
            :props="{ label: 'label', value: 'value', disabled: 'disabled' }"
            multiple
            placeholder="请选择成员"
            clearable
            check-strictly
            :render-after-expand="false"
            style="width: 100%"
            v-loading="deptStore.userListLoading"
          />
        </el-form-item>
        <el-form-item label="状态" prop="enabled">
          <el-radio-group v-model="deptForm.enabled">
            <el-radio :value="0">启用</el-radio>
            <el-radio :value="1">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deptDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDeptForm" :loading="submitLoading">
          {{ formType === 'add' ? '添加' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框（有子部门或用户时） -->
    <el-dialog v-model="deleteDialogVisible" title="删除确认" width="500px" destroy-on-close>
      <el-alert type="warning" :closable="false" show-icon class="delete-warning">
        <template #title> 该组织存在以下关联数据，请先处理后再删除： </template>
      </el-alert>
      <div class="delete-info">
        <p v-if="deleteTargetDept?.childDeptCount && deleteTargetDept.childDeptCount > 0">
          <el-icon>
            <Folder />
          </el-icon>
          子组织：{{ deleteTargetDept.childDeptCount }} 个
        </p>
        <p v-if="deleteTargetDept?.userCount && deleteTargetDept.userCount > 0">
          <el-icon>
            <User />
          </el-icon>
          成员：{{ deleteTargetDept.userCount }} 人
        </p>
      </div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, OfficeBuilding, Folder, User } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type ElTree from 'element-plus/es/components/tree'
import { useDeptStore, type DeptTreeNode, type SysDept } from '@/stores/system/dept'

const deptStore = useDeptStore()

// 树形组件引用
const treeRef = ref<InstanceType<typeof ElTree>>()

// 搜索关键词
const searchKeyword = ref('')

// 选中的部门
const selectedDept = ref<SysDept | null>(null)
// 选中的人员
const selectedUser = ref<DeptTreeNode | null>(null)

// 对话框状态
const deptDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const submitLoading = ref(false)

// 表单类型
const formType = ref<'add' | 'edit'>('add')
const parentDeptId = ref<string | null>(null)
const deleteTargetDept = ref<SysDept | null>(null)

// 表单引用
const deptFormRef = ref<FormInstance>()

// 初始表单数据
const initialDeptForm = {
  deptId: '',
  name: '',
  parentId: '',
  sortOrder: 0,
  enabled: 0 as 0 | 1,
  userIdList: [] as string[],
}

// 部门表单数据
const deptForm = reactive({ ...initialDeptForm })

// 表单验证规则
const deptFormRules: FormRules = {
  name: [
    { required: true, message: '请输入名称', trigger: 'blur' },
    { min: 1, max: 50, message: '名称长度在 1 到 50 个字符', trigger: 'blur' },
  ],
  sortOrder: [
    { required: true, message: '请输入排序值', trigger: 'blur' },
    { type: 'number', min: 0, max: 9999, message: '排序值必须在 0 到 9999 之间', trigger: 'blur' },
  ],
}

// 对话框标题
const dialogTitle = computed(() => {
  return formType.value === 'add' ? '添加组织' : '编辑组织'
})

// 上级部门选项（排除当前编辑的部门及其子部门）
const parentTreeOptions = computed(() => {
  const filterTree = (nodes: DeptTreeNode[]): DeptTreeNode[] => {
    return nodes
      .filter((node) => {
        // 排除当前编辑的部门
        if (formType.value === 'edit' && node.id === deptForm.deptId) {
          return false
        }
        // 只显示部门节点，不显示用户节点
        return node.type === 0
      })
      .map((node) => ({
        ...node,
        children: node.children
          ? filterTree(node.children.filter((child) => child.type === 0))
          : undefined,
      }))
  }

  return filterTree(deptStore.deptTree)
})

// 搜索过滤
const filterNode = (value: string, data: DeptTreeNode) => {
  if (!value) return true
  return data.name.includes(value)
}

// 处理搜索
const handleSearch = (value: string) => {
  treeRef.value?.filter(value)
}

// 处理节点点击
const handleNodeClick = async (data: DeptTreeNode) => {
  if (data.type === 0) {
    // 点击的是部门
    selectedUser.value = null
    const deptDetail = await deptStore.fetchDeptById(data.id)
    if (deptDetail) {
      selectedDept.value = deptDetail
    }
  } else {
    // 点击的是用户
    selectedDept.value = null
    selectedUser.value = data
  }
}

// 处理用户点击
const handleUserClick = (user: any) => {
  selectedDept.value = null
  selectedUser.value = {
    id: user.userId,
    name: user.realName || user.username,
    parentId: user.parentId || '',
    type: 1,
    userId: user.userId,
    username: user.username,
    realName: user.realName,
    phone: user.phone,
    email: user.email,
  }
}

// 添加顶级部门
const handleAddRootDept = async () => {
  formType.value = 'add'
  parentDeptId.value = null
  Object.assign(deptForm, initialDeptForm)
  deptForm.parentId = ''

  // 获取用户列表
  await deptStore.fetchUserTreeForSelect()
  deptDialogVisible.value = true
}

// 添加子部门
const handleAddChildDept = async (parentDept: DeptTreeNode) => {
  formType.value = 'add'
  parentDeptId.value = parentDept.id
  Object.assign(deptForm, initialDeptForm)
  deptForm.parentId = parentDept.id

  // 获取用户列表
  await deptStore.fetchUserTreeForSelect()
  deptDialogVisible.value = true
}

// 编辑部门
const handleEditDept = async (dept: SysDept | DeptTreeNode) => {
  formType.value = 'edit'

  let deptDetail: SysDept | null = null
  if ('deptId' in dept) {
    deptDetail = dept
  } else {
    deptDetail = await deptStore.fetchDeptById(dept.id)
  }

  if (!deptDetail) {
    ElMessage.error('获取详情失败')
    return
  }

  // 填充表单数据
  Object.assign(deptForm, {
    deptId: deptDetail.deptId,
    name: deptDetail.name,
    parentId: deptDetail.parentId === '0' ? '' : deptDetail.parentId,
    sortOrder: deptDetail.sortOrder,
    enabled: deptDetail.enabled,
    userIdList: deptDetail.userList?.map((user) => user.userId) || [],
  })

  // 获取用户列表
  await deptStore.fetchUserTreeForSelect()
  deptDialogVisible.value = true
}

// 删除部门
const handleDeleteDept = async (dept: SysDept | DeptTreeNode) => {
  let deptDetail: SysDept | null = null
  if ('deptId' in dept) {
    deptDetail = dept
  } else {
    deptDetail = await deptStore.fetchDeptById(dept.id)
  }

  if (!deptDetail) {
    ElMessage.error('获取详情失败')
    return
  }

  // 检查是否可以删除
  if (!deptStore.canDeleteDept(deptDetail)) {
    deleteTargetDept.value = deptDetail
    deleteDialogVisible.value = true
    return
  }

  // 可以删除，显示确认对话框
  ElMessageBox.confirm(`确定要删除组织"${deptDetail.name}"吗？此操作不可恢复。`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      const success = await deptStore.deleteDept(deptDetail!.deptId)
      if (success) {
        // 如果删除的是当前选中的部门，清空选中状态
        if (selectedDept.value?.deptId === deptDetail!.deptId) {
          selectedDept.value = null
        }
        // 刷新树形结构
        await deptStore.fetchDeptTree()
      }
    })
    .catch(() => {
      // 用户取消删除
    })
}

// 提交表单
const submitDeptForm = async () => {
  if (!deptFormRef.value || submitLoading.value) return

  try {
    // 使用 Promise 方式验证，避免回调导致的重复执行
    const valid = await deptFormRef.value.validate().catch(() => false)
    if (!valid) return

    submitLoading.value = true

    const deptData = {
      deptId: deptForm.deptId || undefined,
      name: deptForm.name,
      parentId: deptForm.parentId || '0',
      sortOrder: deptForm.sortOrder,
      enabled: deptForm.enabled,
    }

    // 获取成员ID列表
    const userIdList = deptForm.userIdList || []

    let success: boolean
    if (formType.value === 'add') {
      success = await deptStore.addDept(deptData, userIdList)
    } else {
      success = await deptStore.updateDept(deptData, userIdList)
    }

    if (success) {
      deptDialogVisible.value = false
      // 如果编辑的是当前选中的部门，刷新详情
      if (formType.value === 'edit' && selectedDept.value) {
        const deptId = deptForm.deptId
        if (deptId) {
          const detail = await deptStore.fetchDeptById(deptId)
          if (detail) {
            selectedDept.value = detail
          }
        }
      }
    }
  } finally {
    submitLoading.value = false
  }
}

// 对话框关闭
const handleDialogClose = () => {
  deptFormRef.value?.resetFields()
  Object.assign(deptForm, initialDeptForm)
}

// 初始化
onMounted(async () => {
  await deptStore.fetchDeptTree()
})
</script>

<style scoped>
@import '@sys/styles/common.css';
/* 部门管理特定样式 */

.dept-layout {
  display: flex;
  height: 100%;
}

.tree-panel {
  width: 350px;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.tree-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.tree-content {
  flex: 1;
  overflow: auto;
  padding: 8px;
}

.dept-tree {
  background: transparent;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}

.node-content {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.node-icon {
  margin-right: 6px;
  color: #409eff;
}

.node-icon.is-user {
  color: #67c23a;
}

.node-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-count {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 12px;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.node-actions .el-button {
  width: 24px;
  height: 24px;
  min-height: 24px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-actions .el-button .el-icon {
  font-size: 14px;
}

.detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.dept-detail,
.user-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.detail-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item label {
  font-weight: 500;
  color: #909399;
  margin-right: 8px;
  min-width: 80px;
}

.members-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.member-item:hover {
  background: #e9ecef;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #ebeef5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.member-details {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 8px;
}

.member-status {
  margin-left: 8px;
}

.empty-detail {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-warning {
  margin-bottom: 16px;
}

.delete-info {
  padding: 16px;
  background: #fdf6ec;
  border-radius: 8px;
  border: 1px solid #f5dab1;
}

.delete-info p {
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e6a23c;
}

.delete-info .el-icon {
  color: #e6a23c;
}
</style>
