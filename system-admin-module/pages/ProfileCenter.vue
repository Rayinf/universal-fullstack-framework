<template>
  <div class="app-page">
    <!-- 个人信息展示 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3>个人信息</h3>
          <p>查看您的基本信息</p>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="姓名">{{ user?.name || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ user?.username || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ user?.email || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag v-for="role in user?.roles" :key="role" type="primary" style="margin-right: 8px">{{ role }}</el-tag>
          <span v-if="!user?.roles?.length">未设置</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 修改密码 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3>修改密码</h3>
          <p>为了账户安全，请定期修改密码</p>
        </div>
      </template>
      <div class="password-section">
        <el-button type="primary" @click="showPasswordDialog = true" style="width: 120px;">
          修改密码
        </el-button>
        <p class="password-tip">建议定期修改密码以保障账户安全</p>
      </div>
    </el-card>

    <!-- 修改密码弹窗 -->
    <el-drawer
      v-model="showPasswordDialog"
      title="修改密码"
      :size="480"
      direction="rtl"
    >
      <div class="password-drawer-content">
        <el-alert
          title="安全提醒"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 24px;"
        >
          <template #default>
            为了您的账户安全，请设置复杂度较高的密码，并定期更换。
          </template>
        </el-alert>
        
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
          label-position="top"
        >
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input
              v-model="passwordForm.oldPassword"
              type="password"
              placeholder="请输入旧密码"
              show-password
              clearable
              size="large"
            />
          </el-form-item>
          <el-form-item label="新密码" prop="password">
            <el-input
              v-model="passwordForm.password"
              type="password"
              placeholder="请输入新密码（至少6位）"
              show-password
              clearable
              size="large"
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="password1">
            <el-input
              v-model="passwordForm.password1"
              type="password"
              placeholder="请再次输入新密码"
              show-password
              clearable
              size="large"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="showPasswordDialog = false" size="large">取消</el-button>
          <el-button type="primary" @click="handlePasswordSubmit" :loading="passwordLoading" size="large">
            确认修改
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage, ElNotification, type FormInstance } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/modules/auth'
import { updateUserPasswordApi } from '@/api/modules/user'
import type { UserUpdateDto } from '@/types/user'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.userInfo)

// 组件加载时获取最新用户信息
onMounted(async () => {
  try {
    await authStore.fetchProfile()
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
})

// 密码表单
const passwordFormRef = ref<FormInstance>()
const passwordLoading = ref(false)
const showPasswordDialog = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  password: '',
  password1: ''
})

// 密码表单验证规则
const passwordRules = {
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
        if (value !== passwordForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.password = ''
  passwordForm.password1 = ''
  passwordFormRef.value?.clearValidate()
}

// 提交密码修改
const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }
  
  passwordLoading.value = true
  
  try {
    // 确保获取正确的用户ID
    const userId = user.value?.id || ''
    
    console.log('修改密码 - 用户ID:', userId, '用户信息:', user.value)
    
    // 检查 userId 是否有效
    if (!userId) {
      ElMessage.error('无法获取用户ID，请重新登录')
      return
    }
    
    const updateData: UserUpdateDto = {
      userId: userId,
      oldPassword: passwordForm.oldPassword,
      password: passwordForm.password,
      password1: passwordForm.password1
    }
    
    await updateUserPasswordApi(updateData)
    ElNotification.success('密码修改成功，正在跳转到登录页')
    resetPasswordForm()
    showPasswordDialog.value = false
    
    // 密码修改成功后，立即跳转到登录页
    authStore.logout()
    router.push('/login')
    
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('密码修改失败，请检查旧密码是否正确')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.section-card {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.card-header {
  h3 {
    margin: 0 0 4px;
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  
  p {
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
}

.el-descriptions {
  :deep(.el-descriptions__body) {
    .el-descriptions__table {
      .el-descriptions__cell {
        padding: 16px;
        
        &.is-bordered-label {
          background-color: #fafafa;
          font-weight: 500;
          color: var(--el-text-color-regular);
        }
        
        &:not(.is-bordered-label) {
          color: var(--el-text-color-primary);
        }
      }
    }
  }
}

.password-section {
  padding: 24px 0;
  text-align: center;
  
  .el-button {
    margin-bottom: 12px;
  }
  
  .password-tip {
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
}

.password-drawer-content {
  padding: 0 4px;
  
  .el-form {
    .el-form-item {
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .el-form-item__label {
        font-weight: 500;
        color: var(--el-text-color-primary);
        margin-bottom: 8px;
      }
    }
  }
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
  border-top: 1px solid var(--el-border-color-lighter);
  
  .el-button {
    min-width: 100px;
  }
}
</style>
