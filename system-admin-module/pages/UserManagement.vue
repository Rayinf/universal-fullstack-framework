<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>用户列表</h2>
          <div class="page-description">当前共有 {{ total }} 名系统用户，关注角色权限与启停状态。</div>
        </div>
      </div>
      <div class="header-actions">
        <el-tag type="info" style="margin-right: 8px;">已选 {{ selection.length }} 项</el-tag>
        <el-button type="success" @click="handleCreate" style="width: 100px;">新增</el-button>
        <el-button type="danger" :disabled="!selection.length" @click="handleBatchDelete" style="width: 100px;">批量删除</el-button>
      </div>
    </div>

    <div class="search-actions-panel">
      <el-form :model="query" class="filter-form" inline @submit.prevent>
        <!-- <el-form-item label="用户名">
          <el-input v-model="query.username" placeholder="用户名" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item> -->
        <el-form-item label="真实姓名">
          <el-input v-model="query.realName" placeholder="真实姓名" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="query.roleId" placeholder="全部角色" clearable>
            <el-option v-for="item in roleOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.enabled" placeholder="全部状态" clearable>
            <el-option label="启用" :value="0" />
            <el-option label="禁用" :value="1" />
          </el-select>
        </el-form-item>
      </el-form>
      <div class="action-area">
        <el-button type="primary" @click="handleSearch" style="width: 100px;">查询</el-button>
        <el-button @click="handleReset" style="width: 100px;">重置</el-button>
      </div>
    </div>

    <div class="content-card">
      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row @selection-change="handleSelectionChange" class="unified-table">
        <el-table-column type="selection" width="48" />
        <el-table-column prop="username" label="用户名" min-width="140">
          <template #default="{ row }">
            <div class="cell-user">
              <el-avatar :size="28" class="cell-avatar">{{ row.realName?.charAt(0) || row.username?.charAt(0) }}</el-avatar>
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
                style="margin-right: 4px;"
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
        <el-table-column label="操作" fixed="right" width="400" align="center" class-name="col-actions">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" text bg size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="info" text bg size="small" @click="handleResetPassword(row)">重置密码</el-button>
              <el-button 
                :type="row.enabled === 0 ? 'warning' : 'primary'" 
                text bg
                size="small" 
                @click="handleToggleEnabled(row)"
              >
                {{ row.enabled === 0 ? '禁用' : '启用' }}
              </el-button>
              <el-button type="danger" text bg size="small" @click="handleDelete(row)">
                删除
              </el-button>
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

    <!-- 新增用户弹窗 -->
    <FormDialog
      v-model="createUserVisible"
      title="新增用户"
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
            <el-form-item label="用户名" prop="username">
              <el-input v-model="formData.username" placeholder="请输入用户名" />
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
            <el-form-item label="用户角色" prop="role">
              <el-select v-model="formData.role" placeholder="请选择用户角色">
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

    <!-- 编辑用户弹窗 -->
    <FormDialog
      v-model="editUserVisible"
      title="编辑用户"
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
            <el-form-item label="用户名" prop="username">
              <el-input v-model="formData.username" placeholder="请输入用户名" disabled />
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
            <el-form-item label="用户角色" prop="role">
              <el-select v-model="formData.role" placeholder="请选择用户角色">
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
          <el-input v-model="formData.oldPassword" type="password" placeholder="请输入旧密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="formData.password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="password1">
          <el-input v-model="formData.password1" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { request } from '@/api/http'
import { 
  pageUsersApi, 
  createUserApi, 
  updateUserApi, 
  deleteUserApi,
  resetUserPasswordApi,
  updateUserPasswordApi,
  toggleUserEnabledApi
} from '@/api/modules/user'
import type { UserRecord, UserCreateDto, UserUpdateDto, UserPageQuery } from '@/types/user'
import FormDialog from '@/components/common/FormDialog.vue'

interface RoleOption {
  label: string
  value: string
}

const roleOptions = ref<RoleOption[]>([])

const loadRoleOptions = async () => {
  try {
    const res = await request<any>({
      url: '/admin/role/list',
      method: 'get',
    })
    if ((res.code === 0 || res.code === 200) && Array.isArray(res.data)) {
      roleOptions.value = res.data
        .filter((role: any) => role?.roleId !== undefined && role?.roleId !== null && role.delFlag !== '1')
        .map((role: any) => ({
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
  sortType: 'desc'
})

const tableData = ref<UserRecord[]>([])
const selection = ref<UserRecord[]>([])

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const total = computed(() => pagination.total)

const loadData = async () => {
  try {
    const page = {
      records: [],
      total: 0,
      current: pagination.currentPage,
      size: pagination.pageSize,
      optimizeJoinOfCountSql: true,
      pages: 0
    }
    
    const res = await pageUsersApi({ ...page, ...query })
    if (res.code === 200 && res.data) {
      tableData.value = res.data.records || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElNotification.error('加载用户数据失败')
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

const handleSelectionChange = (rows: UserRecord[]) => {
  selection.value = rows
}

// 用户管理功能
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
  role: undefined
})

// 修改密码表单数据
const passwordFormData = reactive({
  userId: 0,
  oldPassword: '',
  password: '',
  password1: ''
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择用户角色', trigger: 'change' }],
}

// 修改密码表单验证规则
const passwordFormRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  password1: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { 
      validator: (_rule: any, value: string, callback: Function) => {
        if (value !== passwordFormData.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

const resetUserForm = () => {
  Object.assign(userFormData, {
    username: '',
    realName: '',
    phone: '',
    email: '',
    password: '',
    role: undefined
  })
}

const resetPasswordForm = () => {
  Object.assign(passwordFormData, {
    userId: 0,
    oldPassword: '',
    password: '',
    password1: ''
  })
}

const handleCreate = () => {
  resetUserForm()
  createUserVisible.value = true
}

const handleCreateUserSubmit = async (data: Record<string, any>) => {
  userFormLoading.value = true
  
  try {
    const createData: UserCreateDto = {
      username: data.username,
      realName: data.realName,
      phone: data.phone,
      email: data.email,
      password: data.password,
      role: data.role ? [data.role] : [] // 将单个角色转换为数组
    }
    
    await createUserApi(createData)
    ElNotification.success('用户创建成功')
    createUserVisible.value = false
    resetUserForm()
    loadData()
    
  } catch (error) {
    console.error('创建用户失败:', error)
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
  
  console.log('编辑用户调试信息:', {
    原始用户数据: row,
    角色列表: row.roleList,
    直接角色ID: row.roleId,
    转换后的角色ID: roleId,
    角色选项: roleOptions
  })
  
  // 直接设置编辑数据，不调用resetUserForm避免覆盖
  userFormData.username = row.username || ''
  userFormData.realName = row.realName || ''
  userFormData.phone = row.phone || ''
  userFormData.email = row.email || ''
  userFormData.password = '' // 编辑时密码为空
  userFormData.role = roleId
  
  console.log('表单数据设置后:', {
    username: userFormData.username,
    realName: userFormData.realName,
    phone: userFormData.phone,
    role: userFormData.role
  })
  
  editUserVisible.value = true
}

const handleEditUserSubmit = async (data: Record<string, any>) => {
  userFormLoading.value = true
  
  try {
    const updateData: UserUpdateDto = {
      userId: currentUser.value?.userId || 0,
      realName: data.realName,
      phone: data.phone,
      email: data.email,
      role: data.role ? [data.role] : [] // 将单个角色转换为数组
    }
    
    await updateUserApi(updateData)
    ElNotification.success('用户信息更新成功')
    editUserVisible.value = false
    resetUserForm()
    loadData()
    
  } catch (error) {
    console.error('更新用户失败:', error)
    // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
  } finally {
    userFormLoading.value = false
  }
}

const handleDelete = async (row: UserRecord) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除用户 ${row.username} 吗？删除后将无法恢复！`,
      '删除用户',
      { 
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        customClass: 'custom-message-box'
      }
    )
    
    await deleteUserApi(row.userId)
    ElNotification.success(`用户 ${row.username} 已删除`)
    loadData()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
    }
  }
}


const handleChangePasswordSubmit = async (data: Record<string, any>) => {
  passwordFormLoading.value = true
  
  try {
    const updateData: UserUpdateDto = {
      userId: data.userId,
      oldPassword: data.oldPassword,
      password: data.password,
      password1: data.password1
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
      `确认要重置用户 ${row.username} (${row.realName}) 的密码吗？重置后密码将恢复为初始密码。`,
      '重置密码',
      { 
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        customClass: 'custom-message-box'
      }
    )
    
    await resetUserPasswordApi(row.userId)
    ElNotification.success(`用户 ${row.username} 的密码已重置为初始密码`)
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
    }
  }
}

const handleBatchDelete = async () => {
  if (selection.value.length === 0) {
    ElNotification.warning('请先选择要删除的用户')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认要删除选中的 ${selection.value.length} 个用户吗？删除后将无法恢复！`,
      '批量删除用户',
      { 
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        customClass: 'custom-message-box'
      }
    )
    
    // 批量删除用户
    const deletePromises = selection.value.map(user => deleteUserApi(user.userId))
    await Promise.all(deletePromises)
    
    // 清空选择
    selection.value = []
    
    ElNotification.success(`已成功删除 ${selection.value.length} 个用户`)
    loadData()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      // HTTP拦截器已经处理了错误消息显示，这里不需要重复显示
    }
  }
}

const handleToggleEnabled = async (row: UserRecord) => {
  const newStatus = row.enabled === 0 ? 1 : 0
  const actionText = newStatus === 0 ? '启用' : '禁用'
  
  try {
    await ElMessageBox.confirm(
      `确认要${actionText}用户 ${row.username} (${row.realName}) 吗？`,
      `${actionText}用户`,
      { 
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        customClass: 'custom-message-box'
      }
    )
    
    await toggleUserEnabledApi(row.userId, newStatus)
    ElNotification.success(`用户 ${row.username} 已${actionText}`)
    loadData()
    
  } catch (error) {
    if (error !== 'cancel') {
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
.filter-form {
  flex: 1;
}

.page-toolbar__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0 0 4px;
    font-size: 18px;
  }

  p {
    margin: 0;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
}

.cell-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cell-avatar {
  background: rgba(35, 116, 248, 0.08);
  color: var(--el-color-primary);
  font-weight: 600;
}

.cell-username {
  font-weight: 600;
}

.cell-sub {
  font-size: 12px;
  color: var(--el-text-color-secondary);
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
