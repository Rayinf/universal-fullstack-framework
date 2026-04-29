<template>
  <div
    v-if="visible"
    class="profile-dialog"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @click.stop
  >
    <div class="profile-dialog__header">
      <h3>{{ showPasswordForm ? '修改密码' : '个人信息' }}</h3>
      <el-button type="text" size="small" @click="handleClose" class="profile-dialog__close">
        <!-- <el-icon><Close /></el-icon> -->
      </el-button>
    </div>

    <div class="profile-dialog__content">
      <!-- 个人信息视图 -->
      <div v-if="!showPasswordForm">
        <div class="profile-avatar">
          <div class="avatar-circle">
            <span>{{ userInitial }}</span>
          </div>
        </div>

        <div class="profile-info">
          <div class="info-item">
            <label>姓名</label>
            <span>{{ user?.name || '未设置' }}</span>
          </div>

          <div class="info-item">
            <label>用户名</label>
            <span>{{ user?.username || '未设置' }}</span>
          </div>

          <div class="info-item">
            <label>邮箱</label>
            <span>{{ user?.email || '未设置' }}</span>
          </div>

          <div class="info-item">
            <label>电话</label>
            <span>{{ user?.phone || '未设置' }}</span>
          </div>

          <div class="info-item">
            <label>角色</label>
            <div class="roles">
              <el-tag size="small" type="info">
                {{ user?.role || '未设置' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 修改密码视图 -->
      <div v-else class="password-form-container">
        <div class="password-header">
          <p>为了账户安全，请设置复杂度较高的密码</p>
        </div>

        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="80px"
          label-position="top"
        >
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input
              v-model="passwordForm.oldPassword"
              type="password"
              placeholder="请输入旧密码"
              show-password
              clearable
            />
          </el-form-item>
          <el-form-item label="新密码" prop="password">
            <el-input
              v-model="passwordForm.password"
              type="password"
              placeholder="请输入新密码（至少6位）"
              show-password
              clearable
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="password1">
            <el-input
              v-model="passwordForm.password1"
              type="password"
              placeholder="请再次输入新密码"
              show-password
              clearable
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="profile-dialog__footer">
      <!-- 个人信息视图的按钮 -->
      <template v-if="!showPasswordForm">
        <el-button size="small" @click="handleClose">关闭</el-button>
        <el-button type="primary" size="small" @click="handleChangePassword">修改密码</el-button>
      </template>

      <!-- 修改密码视图的按钮 -->
      <template v-else>
        <el-button size="small" @click="handleBackToInfo">返回</el-button>
        <el-button
          type="primary"
          size="small"
          @click="handlePasswordSubmit"
          :loading="passwordLoading"
        >
          确认修改
        </el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, nextTick } from 'vue'
import { ElMessage, ElNotification, type FormInstance } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { updateUserPasswordApi } from '@/api/system/user'
import type { UserUpdateDto } from '@/types/system/user'

interface Props {
  visible: boolean
  triggerElement?: HTMLElement | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => {
  console.log('ProfileDialog中的用户信息:', userStore.currentUser)
  return userStore.currentUser
})
const userInitial = computed(() => (user.value?.name ?? user.value?.username ?? '用').slice(0, 1))

// 角色名称通过 userStore.currentUser?.role 直接获取（后端已返回角色名称）

// 密码修改相关
const showPasswordForm = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordLoading = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  password: '',
  password1: '',
})

// 密码表单验证规则
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
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
      trigger: 'blur',
    },
  ],
}

const position = ref({ x: 0, y: 0 })

// 计算弹窗位置
const calculatePosition = () => {
  if (!props.triggerElement) return

  const rect = props.triggerElement.getBoundingClientRect()
  const dialogWidth = 420
  const dialogHeight = 400

  let x = rect.right - dialogWidth + 10 // 右对齐，稍微向左偏移
  let y = rect.bottom + 8 // 在触发元素下方

  // 边界检测
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  // 水平边界检测
  if (x + dialogWidth > viewportWidth) {
    x = viewportWidth - dialogWidth - 16
  }
  if (x < 16) {
    x = 16
  }

  // 垂直边界检测
  if (y + dialogHeight > viewportHeight) {
    y = rect.top - dialogHeight - 8 // 显示在触发元素上方
  }
  if (y < 16) {
    y = 16
  }

  position.value = { x, y }
}

// 监听 visible 变化，计算位置
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      nextTick(() => {
        calculatePosition()
      })
    }
  },
)

const handleClose = () => {
  showPasswordForm.value = false
  resetPasswordForm()
  emit('update:visible', false)
}

const handleChangePassword = () => {
  showPasswordForm.value = true
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
    // 确保获取正确的用户ID（使用 string 类型避免大数字精度丢失）
    const userId = user.value?.id || ''

    if (!userId) {
      ElMessage.error('无法获取用户ID，请重新登录')
      return
    }

    const updateData: UserUpdateDto = {
      userId: userId,
      oldPassword: passwordForm.oldPassword,
      password: passwordForm.password,
      password1: passwordForm.password1,
    }

    await updateUserPasswordApi(updateData)
    ElNotification.success('密码修改成功，正在跳转到登录页')
    handleClose()

    // 密码修改成功后，立即跳转到登录页
    userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('密码修改失败，请检查旧密码是否正确')
  } finally {
    passwordLoading.value = false
  }
}

const handleBackToInfo = () => {
  showPasswordForm.value = false
  resetPasswordForm()
}
</script>

<style lang="scss" scoped>
.profile-dialog {
  position: fixed;
  width: 420px;
  min-width: 420px;
  background: #fff;
  border-radius: 16px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.12),
    0 8px 24px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.06);
  z-index: 2000;
  overflow: hidden;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-12px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.profile-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);
  min-height: 60px;

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    letter-spacing: -0.025em;
    line-height: 1.2;
    white-space: nowrap;
    min-width: 0;
    flex-shrink: 0;
  }
}

.profile-dialog__close {
  padding: 8px;
  color: #6b7280;
  border-radius: 8px;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-left: 16px;

  &:hover {
    color: #374151;
    background: rgba(0, 0, 0, 0.05);
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }
}

.profile-dialog__content {
  padding: 24px;
}

.profile-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 28px;

  .avatar-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 28px;
    font-weight: 700;
    box-shadow:
      0 8px 24px rgba(59, 130, 246, 0.25),
      0 4px 12px rgba(29, 78, 216, 0.15);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      inset: -2px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      z-index: -1;
      opacity: 0.3;
      filter: blur(8px);
    }
  }
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;

  &:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-1px);
  }

  label {
    font-size: 11px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 2px;
  }

  span {
    font-size: 15px;
    color: #1e293b;
    font-weight: 500;
    line-height: 1.4;

    &.no-data {
      color: #94a3b8;
      font-style: italic;
      font-weight: 400;
    }
  }
}

.roles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 2px;

  .el-tag {
    border-radius: 20px;
    font-weight: 500;
    font-size: 12px;
    padding: 4px 12px;
    border: none;
    background: #6b7280;
    color: #fff;
    box-shadow: 0 2px 8px rgba(107, 114, 128, 0.2);
  }
}

.profile-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%);

  .el-button {
    border-radius: 10px;
    font-weight: 500;
    padding: 8px 20px;
    transition: all 0.2s ease;

    &:not(.el-button--primary) {
      background: #fff;
      border-color: #d1d5db;
      color: #6b7280;

      &:hover {
        background: #f9fafb;
        border-color: #9ca3af;
        color: #374151;
        transform: translateY(-1px);
      }
    }

    &.el-button--primary {
      background: #374151;
      border: none;
      box-shadow: 0 4px 12px rgba(55, 65, 81, 0.3);

      &:hover {
        background: #4b5563;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(55, 65, 81, 0.4);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}

.password-form-container {
  .password-header {
    text-align: center;
    margin-bottom: 24px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 12px;
    border: 1px solid #e2e8f0;

    p {
      margin: 0;
      font-size: 14px;
      color: #64748b;
      line-height: 1.5;
    }
  }

  .el-form {
    .el-form-item {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .el-form-item__label {
        font-weight: 500;
        color: var(--el-text-color-primary);
        margin-bottom: 6px;
      }

      .el-input {
        .el-input__wrapper {
          border-radius: 8px;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 480px) {
  .profile-dialog {
    width: calc(100vw - 32px);
    max-width: 420px;
    min-width: 360px;
  }

  .profile-dialog__content {
    padding: 20px;
  }

  .profile-avatar .avatar-circle {
    width: 70px;
    height: 70px;
    font-size: 24px;
  }

  .info-item {
    padding: 10px 14px;
  }
}
</style>
