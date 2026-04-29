<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>账户管理</h2>
          <div class="page-description">管理系统账户信息，包括创建、编辑、删除账户及权限分配。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form :model="query" class="filter-form" inline @submit.prevent>
          <el-form-item label="真实姓名">
            <el-input v-model="query.realName" placeholder="真实姓名" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="query.roleId" placeholder="全部角色" clearable style="width: 160px">
              <el-option
                v-for="item in roleOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="query.enabled"
              placeholder="全部状态"
              clearable
              style="width: 120px"
            >
              <el-option label="启用" :value="0" />
              <el-option label="禁用" :value="1" />
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
        <div class="action-area">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>新增账户
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table
          :data="tableData"
          v-loading="tableLoading"
          stripe
          highlight-current-row
          class="unified-table"
        >
          <el-table-column prop="username" label="账户名" min-width="140">
            <template #default="{ row }">
              <div class="cell-user">
                <el-avatar :size="28" class="cell-avatar">{{
                  row.realName?.charAt(0) || row.username?.charAt(0)
                }}</el-avatar>
                <div>
                  <div class="cell-username">{{ row.username }}</div>
                  <div class="cell-sub">{{ row.realName }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="role" label="角色" width="140">
            <template #default="{ row }">
              <!-- 如果有roleList，显示roleList中的角色 -->
              <template v-if="row.roleList && row.roleList.length > 0">
                <el-tag
                  v-for="role in row.roleList"
                  :key="role.roleId"
                  type="primary"
                  effect="plain"
                  style="margin-right: 4px"
                >
                  {{ role.roleName }}
                </el-tag>
              </template>
              <!-- 如果没有roleList但有roleId，根据roleId显示角色名称 -->
              <template v-else-if="row.roleId">
                <el-tag type="primary" effect="plain">
                  {{ roleOptions.find((r) => r.value === String(row.roleId))?.label || '未知角色' }}
                </el-tag>
              </template>
              <!-- 都没有的情况 -->
              <template v-else>
                <el-tag type="info" effect="plain">无角色</el-tag>
              </template>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180">
            <template #default="{ row }">
              <span>{{ row.email || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.enabled === 0 ? 'success' : 'danger'" effect="dark">
                {{ row.enabled === 0 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" min-width="180" />
          <el-table-column
            label="操作"
            fixed="right"
            width="320"
            align="center"
            class-name="col-actions"
          >
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
                <!-- <el-button link type="info" @click="handleChangePassword(row)">修改密码</el-button> -->
                <el-button link type="warning" @click="handleResetPassword(row)"
                  >重置密码</el-button
                >
                <el-button
                  link
                  :type="row.enabled === 0 ? 'warning' : 'success'"
                  @click="handleToggleEnabled(row)"
                >
                  {{ row.enabled === 0 ? '禁用' : '启用' }}
                </el-button>
                <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 新增账户弹窗 -->
    <FormDialog
      v-model="createUserVisible"
      title="新增账户"
      :form-data="userFormData"
      :rules="userFormRules"
      :loading="userFormLoading"
      width="600px"
      @submit="handleCreateUserSubmit"
      @cancel="createUserVisible = false"
    >
      <template #default="{ formData }">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="账户名" prop="username">
              <el-input v-model="formData.username" placeholder="请输入账户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="formData.realName" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input v-model="formData.password" type="password" placeholder="请输入密码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="账户角色" prop="role">
              <el-select v-model="formData.role" placeholder="请选择账户角色">
                <el-option
                  v-for="role in roleOptions"
                  :key="role.value"
                  :label="role.label"
                  :value="role.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </FormDialog>

    <!-- 编辑账户弹窗 -->
    <FormDialog
      v-model="editUserVisible"
      title="编辑账户"
      :form-data="userFormData"
      :rules="userFormRules"
      :loading="userFormLoading"
      width="600px"
      @submit="handleEditUserSubmit"
      @cancel="editUserVisible = false"
    >
      <template #default="{ formData }">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="账户名" prop="username">
              <el-input v-model="formData.username" placeholder="请输入账户名" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="formData.realName" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="账户角色" prop="role">
              <el-select v-model="formData.role" placeholder="请选择账户角色">
                <el-option
                  v-for="role in roleOptions"
                  :key="role.value"
                  :label="role.label"
                  :value="role.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </FormDialog>

    <!-- 修改密码弹窗 -->
    <FormDialog
      v-model="changePasswordVisible"
      title="修改密码"
      :form-data="passwordFormData"
      :rules="passwordFormRules"
      :loading="passwordFormLoading"
      width="500px"
      @submit="handleChangePasswordSubmit"
      @cancel="changePasswordVisible = false"
    >
      <template #default="{ formData }">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            v-model="formData.oldPassword"
            type="password"
            placeholder="请输入旧密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="password1">
          <el-input
            v-model="formData.password1"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import type { FormItemRule } from 'element-plus'
import { Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import {
  pageUsersApi,
  createUserApi,
  updateUserApi,
  deleteUserApi,
  resetUserPasswordApi,
  updateUserPasswordApi,
  toggleUserEnabledApi,
} from '@/api/system/user'
import { getRoleListApi } from '@/api/system/role'
import type { UserRecord, UserCreateDto, UserUpdateDto, UserPageQuery } from '@/types/system/user'
import FormDialog from '@/components/system/FormDialog.vue'
import { isSuccessCode } from '@/utils/apiResponse'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface RoleOption {
  label: string
  value: string
}

interface PasswordFormData {
  userId: string
  oldPassword: string
  password: string
  password1: string
}

interface UserFormSubmitData {
  username: string
  realName: string
  phone?: string
  email?: string
  password?: string
  role?: string | string[]
}

const roleOptions = ref<RoleOption[]>([])

const loadRoleOptions = async () => {
  try {
    const res = await getRoleListApi()
    if ((res.code === 0 || res.code === 200) && Array.isArray(res.data)) {
      roleOptions.value = res.data
        .filter(
          (role) => role?.roleId !== undefined && role?.roleId !== null && role.delFlag !== '1',
        )
        .map((role) => ({
          label: role.roleName,
          value: String(role.roleId),
        }))
      return
    }
    roleOptions.value = []
  } catch (error) {
    console.error('加载角色选项失败:', error)
    roleOptions.value = []
  }
}

const query = reactive<UserPageQuery>({
  username: '',
  realName: '',
  roleId: undefined,
  enabled: undefined,
  sortColumn: 'create_time',
  sortType: 'desc',
})

const tableData = ref<UserRecord[]>([])
const tableLoading = ref(false)

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
})

const total = computed(() => pagination.total)

const loadData = async () => {
  tableLoading.value = true
  try {
    const page = {
      records: [],
      total: 0,
      current: pagination.currentPage,
      size: pagination.pageSize,
      optimizeJoinOfCountSql: true,
      pages: 0,
    }

    const res = await pageUsersApi({ ...page, ...query })
    if (isSuccessCode(res.code) && res.data) {
      tableData.value = (res.data.records || []).map((item) => ({
        ...item,
        userId: String(item.userId || ''),
        roleId: item.roleId !== undefined && item.roleId !== null ? String(item.roleId) : undefined,
      }))
      pagination.total = res.data.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('加载账户数据失败:', error)
    ElNotification.error('加载账户数据失败')
    tableData.value = []
    pagination.total = 0
  } finally {
    tableLoading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  query.username = ''
  query.realName = ''
  query.roleId = undefined
  query.enabled = undefined
  pagination.currentPage = 1
  loadData()
}

// 分页事件处理
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadData()
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadData()
}

// 账户管理功能
const createUserVisible = ref(false)
const editUserVisible = ref(false)
const changePasswordVisible = ref(false)
const userFormLoading = ref(false)
const passwordFormLoading = ref(false)
const currentUser = ref<UserRecord | null>(null)

const userFormData = reactive<UserCreateDto>({
  username: '',
  realName: '',
  phone: '',
  email: '',
  password: '',
  role: undefined,
})

// 修改密码表单数据
const passwordFormData = reactive<PasswordFormData>({
  userId: '',
  oldPassword: '',
  password: '',
  password1: '',
})

const userFormRules = {
  username: [
    { required: true, message: '请输入账户名', trigger: 'blur' },
    { min: 3, max: 20, message: '账户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' },
  ],
  email: [
    { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择账户角色', trigger: 'change' }],
}

// 修改密码表单验证规则
const passwordFormRules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  password1: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule: FormItemRule, value: string, callback: (error?: Error) => void) => {
        if (value !== passwordFormData.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const resetUserForm = () => {
  Object.assign(userFormData, {
    username: '',
    realName: '',
    phone: '',
    email: '',
    password: '',
    role: undefined,
  })
}

const resetPasswordForm = () => {
  Object.assign(passwordFormData, {
    userId: '',
    oldPassword: '',
    password: '',
    password1: '',
  })
}

const handleCreate = () => {
  resetUserForm()
  createUserVisible.value = true
}

const normalizeRoleValue = (role: string | string[] | undefined): string[] => {
  if (!role) return []
  return Array.isArray(role) ? role.filter((item): item is string => Boolean(item)) : [role]
}

const handleCreateUserSubmit = async (data: Record<string, any>) => {
  userFormLoading.value = true

  try {
    const formData = data as UserFormSubmitData
    const createData: UserCreateDto = {
      username: formData.username,
      realName: formData.realName,
      phone: formData.phone,
      email: formData.email,
      password: formData.password || '',
      role: normalizeRoleValue(formData.role),
    }

    await createUserApi(createData)
    ElNotification.success('账户创建成功')
    createUserVisible.value = false
    resetUserForm()
    loadData()
  } catch (error) {
    console.error('创建账户失败:', error)
    // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
  } finally {
    userFormLoading.value = false
  }
}

const handleEdit = (row: UserRecord) => {
  currentUser.value = row

  // 处理角色数据：优先使用roleList，如果没有则使用roleId字段
  let roleId: string | undefined

  if (row.roleList && row.roleList.length > 0) {
    // 如果有roleList，取第一个角色的roleId
    const firstRole = row.roleList[0]
    if (firstRole) {
      roleId = String(firstRole.roleId)
    }
  } else if (row.roleId) {
    // 如果没有roleList但有roleId字段，直接使用roleId
    roleId = String(row.roleId)
  }

  // 直接设置编辑数据，不调用resetUserForm避免覆盖
  userFormData.username = row.username || ''
  userFormData.realName = row.realName || ''
  userFormData.phone = row.phone || ''
  userFormData.email = row.email || ''
  userFormData.password = '' // 编辑时密码为空
  userFormData.role = roleId

  editUserVisible.value = true
}

const handleEditUserSubmit = async (data: Record<string, any>) => {
  userFormLoading.value = true

  try {
    const formData = data as UserFormSubmitData
    const updateData: UserUpdateDto = {
      userId: String(currentUser.value?.userId || ''),
      realName: formData.realName,
      phone: formData.phone,
      email: formData.email,
      role: normalizeRoleValue(formData.role),
    }

    await updateUserApi(updateData)
    ElNotification.success('账户信息更新成功')
    editUserVisible.value = false
    resetUserForm()
    loadData()
  } catch (error) {
    console.error('更新账户失败:', error)
    // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
  } finally {
    userFormLoading.value = false
  }
}

const handleDelete = async (row: UserRecord) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除账户 ${row.username} 吗？删除后将无法恢复！`,
      '删除账户',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        customClass: 'custom-message-box',
      },
    )

    await deleteUserApi(String(row.userId))
    ElNotification.success(`账户 ${row.username} 已删除`)
    loadData()
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('删除账户失败:', error)
      // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
    }
  }
}

const handleChangePasswordSubmit = async (data: Record<string, any>) => {
  passwordFormLoading.value = true

  try {
    const formData = data as PasswordFormData
    const updateData: UserUpdateDto = {
      userId: formData.userId,
      oldPassword: formData.oldPassword,
      password: formData.password,
      password1: formData.password1,
    }

    await updateUserPasswordApi(updateData)
    ElNotification.success('密码修改成功')
    changePasswordVisible.value = false
    resetPasswordForm()
  } catch (error) {
    console.error('修改密码失败:', error)
    ElNotification.error('密码修改失败，请检查旧密码是否正确')
  } finally {
    passwordFormLoading.value = false
  }
}

const handleResetPassword = async (row: UserRecord) => {
  try {
    await ElMessageBox.confirm(
      `确认要重置账户 ${row.username} (${row.realName}) 的密码吗？重置后密码将恢复为初始密码。`,
      '重置密码',
      {
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        customClass: 'custom-message-box',
      },
    )

    await resetUserPasswordApi(String(row.userId))
    ElNotification.success(`账户 ${row.username} 的密码已重置为初始密码`)
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('重置密码失败:', error)
      // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
    }
  }
}

const handleToggleEnabled = async (row: UserRecord) => {
  const newStatus = row.enabled === 0 ? 1 : 0
  const actionText = newStatus === 0 ? '启用' : '禁用'

  try {
    await ElMessageBox.confirm(
      `确认要${actionText}账户 ${row.username} (${row.realName}) 吗？`,
      `${actionText}账户`,
      {
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        customClass: 'custom-message-box',
      },
    )

    await toggleUserEnabledApi(String(row.userId), newStatus)
    ElNotification.success(`账户 ${row.username} 已${actionText}`)
    loadData()
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error(`${actionText}用户失败:`, error)
      // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
    }
  }
}

// 初始化数据加载
onMounted(async () => {
  await loadRoleOptions()
  loadData()
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);
  gap: 16px;
}

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

.action-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cell-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cell-avatar {
  background: rgba(64, 158, 255, 0.1);
  color: var(--el-color-primary);
  font-weight: 600;
}

.cell-username {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.cell-sub {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>

<style lang="scss">
/* 全局样式：修复MessageBox按钮宽度 */
.custom-message-box {
  .el-message-box__btns {
    .el-button {
      min-width: 70px !important;
      max-width: 100px !important;
      padding: 8px 16px !important;
    }
  }
}
</style>
