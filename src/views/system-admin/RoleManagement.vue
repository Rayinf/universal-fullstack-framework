<template>
  <div class="page-view">
    <!-- 统一页面头部 -->
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>用户角色管理</h2>
          <div class="page-description">管理系统用户角色及其权限配置。</div>
        </div>
      </div>
    </div>

    <!-- 页面内容卡片 -->
    <div class="content-card">
      <!-- 搜索操作面板 -->
      <div class="search-actions-panel">
        <el-form :model="query" inline class="filter-form" @submit.prevent>
          <el-form-item label="角色名称">
            <el-input
              v-model="query.roleName"
              placeholder="请输入角色名称"
              clearable
              style="width: 200px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
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
          <el-button type="primary" :icon="Plus" @click="handleCreate"> 新增角色 </el-button>
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
          <el-table-column prop="roleName" label="角色名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="roleCode" label="角色标识" width="150" />
          <el-table-column prop="roleDesc" label="角色描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column label="操作" width="250" fixed="right" align="center">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">
                  编辑
                </el-button>
                <el-button type="primary" link :icon="Setting" @click="handlePermission(row)">
                  权限
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

    <!-- 角色新增/编辑弹窗 -->
    <FormDialog
      v-model="formVisible"
      :title="isEdit ? '编辑角色' : '新增角色'"
      :form-data="formData"
      :rules="formRules"
      :loading="submitLoading"
      width="500px"
      @submit="handleFormSubmit"
    >
      <template #default="{ formData }">
        <el-form-item label="角色名称" prop="roleName">
          <el-input v-model="formData.roleName" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色标识" prop="roleCode">
          <el-input v-model="formData.roleCode" placeholder="请输入角色标识 (如: ROLE_ADMIN)" />
        </el-form-item>
        <el-form-item label="角色描述" prop="roleDesc">
          <el-input
            v-model="formData.roleDesc"
            type="textarea"
            rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
      </template>
    </FormDialog>

    <!-- 权限配置弹窗 -->
    <BaseDialog
      v-model="permissionVisible"
      title="配置角色权限"
      width="600px"
      :loading="permissionSubmitLoading"
      confirm-text="保存配置"
      @confirm="handlePermissionSubmit"
    >
      <div v-loading="permissionLoading">
        <el-alert
          v-if="currentRole"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #title>
            正在为角色 <strong>{{ currentRole.roleName }}</strong> 配置菜单访问权限
          </template>
        </el-alert>

        <el-tree
          ref="treeRef"
          :data="menuTree"
          :props="{ label: 'label', children: 'children' }"
          node-key="id"
          show-checkbox
          default-expand-all
          :check-strictly="false"
          class="permission-tree"
        />
      </div>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type ElTree from 'element-plus/es/components/tree'
import { Search, RefreshLeft, Plus, Edit, Delete, Setting } from '@element-plus/icons-vue'
import type { SysRole, RolePageQuery } from '@/types/system/role'
import type { MenuNode } from '@/types/system/menu'
import {
  getRolePageApi,
  addRoleApi,
  updateRoleApi,
  deleteRoleApi,
  updateRoleMenusApi,
} from '@/api/system/role'
import { getMenuTreeApi, getRoleMenuIdsApi } from '@/api/system/menu'
import FormDialog from '@/components/common/FormDialog.vue'
import BaseDialog from '@/components/common/BaseDialog.vue'
import { usePageQuery } from '@/composables/usePageQuery'
import { isMessageBoxCancel } from '@/utils/elementPlus'

// --- 状态变量 ---
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<SysRole[]>([])
const { query, pagination, loadData, handleSearch, handleReset, handleSizeChange, handleCurrentChange } =
  usePageQuery<RolePageQuery>({
    initialQuery: {
      roleName: '',
    },
    load: async ({ query, pagination }) => {
      loading.value = true
      try {
        const res = await getRolePageApi({
          ...query,
          current: pagination.current,
          size: pagination.size,
        })
        if ((res.code === 0 || res.code === 200) && res.data) {
          tableData.value = res.data.records || []
          pagination.total = res.data.total || 0
        } else {
          tableData.value = []
          pagination.total = 0
          ElMessage.error(res.msg || '获取角色列表失败')
        }
      } catch (error) {
        console.error('获取角色列表失败:', error)
        tableData.value = []
        pagination.total = 0
        ElMessage.error('获取角色列表失败')
      } finally {
        loading.value = false
      }
    },
  })

// 表单相关
const formVisible = ref(false)
const isEdit = ref(false)
const formData = reactive<Partial<SysRole>>({
  roleId: undefined,
  roleName: '',
  roleCode: '',
  roleDesc: '',
})

const formRules = {
  roleName: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  roleCode: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
  roleDesc: [{ required: true, message: '请输入角色描述', trigger: 'blur' }],
}

// 权限配置相关
const permissionVisible = ref(false)
const permissionLoading = ref(false)
const permissionSubmitLoading = ref(false)
const currentRole = ref<SysRole | null>(null)
const menuTree = ref<MenuNode[]>([])
const treeRef = ref<InstanceType<typeof ElTree>>()

// --- 方法 ---

// 新增/编辑
const handleCreate = () => {
  isEdit.value = false
  Object.assign(formData, {
    roleId: undefined,
    roleName: '',
    roleCode: '',
    roleDesc: '',
  })
  formVisible.value = true
}

const handleEdit = (row: SysRole) => {
  isEdit.value = true
  Object.assign(formData, {
    roleId: row.roleId,
    roleName: row.roleName,
    roleCode: row.roleCode,
    roleDesc: row.roleDesc,
  })
  formVisible.value = true
}

const handleFormSubmit = async () => {
  submitLoading.value = true
  try {
    let res
    if (isEdit.value && formData.roleId) {
      res = await updateRoleApi(formData)
    } else {
      res = await addRoleApi(formData)
    }

    if (res.code === 0 || res.code === 200) {
      ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
      formVisible.value = false
      await loadData()
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (error) {
    console.error('提交表单失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: SysRole) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色 "${row.roleName}" 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    const res = await deleteRoleApi(row.roleId)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('删除成功')
      if (tableData.value.length === 1 && pagination.current > 1) {
        pagination.current -= 1
      }
      await loadData()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 收集菜单树中所有非叶子节点（有 children 且 children 非空）的 ID
 */
const collectParentIds = (nodes: MenuNode[]): Set<string> => {
  const parentIds = new Set<string>()
  for (const node of nodes) {
    if (node.children && node.children.length > 0) {
      parentIds.add(String(node.id))
      const childParents = collectParentIds(node.children)
      childParents.forEach((id) => parentIds.add(id))
    }
  }
  return parentIds
}

const handlePermission = async (row: SysRole) => {
  currentRole.value = row
  permissionVisible.value = true
  permissionLoading.value = true

  try {
    const [menuRes, roleMenuRes] = await Promise.all([
      getMenuTreeApi(),
      getRoleMenuIdsApi(row.roleId),
    ])

    if (menuRes.code === 0 || menuRes.code === 200) {
      menuTree.value = menuRes.data || []
    }

    if (roleMenuRes.code === 0 || roleMenuRes.code === 200) {
      const allIds: string[] = (roleMenuRes.data || []).map(String)
      // check-strictly=false 模式下只传叶子节点 ID，父节点会自动联动
      const parentIds = collectParentIds(menuTree.value)
      const leafIds = allIds.filter((id) => !parentIds.has(id))

      nextTick(() => {
        treeRef.value?.setCheckedKeys(leafIds, false)
      })
    }
  } catch (error) {
    console.error('加载权限数据失败:', error)
    ElMessage.error('加载权限数据失败')
  } finally {
    permissionLoading.value = false
  }
}

const handlePermissionSubmit = async () => {
  if (!currentRole.value) return

  permissionSubmitLoading.value = true
  try {
    // 获取选中的节点ID（包括半选状态的父节点）
    const checkedKeys = treeRef.value?.getCheckedKeys() || []
    const halfCheckedKeys = treeRef.value?.getHalfCheckedKeys() || []
    const allKeys = [...checkedKeys, ...halfCheckedKeys]

    const res = await updateRoleMenusApi({
      roleId: currentRole.value.roleId,
      menuIds: allKeys.join(','),
    })

    if (res.code === 0 || res.code === 200) {
      ElMessage.success('权限配置成功')
      permissionVisible.value = false
    } else {
      ElMessage.error(res.msg || '权限配置失败')
    }
  } catch (error) {
    console.error('配置权限失败:', error)
    ElMessage.error('发生网络错误')
  } finally {
    permissionSubmitLoading.value = false
  }
}

onMounted(() => {
  loadData()
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

.permission-tree {
  margin-top: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
  background-color: #fff;
}
</style>
