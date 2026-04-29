<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button link @click="$router.back()" class="back-btn">
              <el-icon><ArrowLeft /></el-icon> 返回
            </el-button>
            <h2>个人中心</h2>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 个人信息标签页 -->
        <el-tab-pane label="个人信息" name="info">
          <el-form
            ref="userFormRef"
            :model="userForm"
            :rules="userFormRules"
            label-width="100px"
            label-position="right"
          >
            <el-form-item label="头像" prop="avatar">
              <el-avatar
                :size="100"
                class="user-avatar"
                :style="{ backgroundColor: 'var(--el-color-primary)', fontSize: '40px' }"
              >
                {{
                  userForm.realName
                    ? userForm.realName.charAt(0)
                    : userForm.username
                      ? userForm.username.charAt(0).toUpperCase()
                      : ''
                }}
              </el-avatar>
            </el-form-item>

            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>

            <el-form-item label="姓名" prop="realName">
              <el-input v-model="userForm.realName" :disabled="!isEditing" />
            </el-form-item>

            <el-form-item label="职位" prop="role">
              <el-input v-model="userForm.role" disabled />
            </el-form-item>

            <el-form-item label="区域" prop="region">
              <el-input v-model="userForm.region" disabled />
            </el-form-item>

            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="userForm.phone" :disabled="!isEditing" />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="userForm.email" :disabled="!isEditing" />
            </el-form-item>

            <el-form-item>
              <el-button v-if="!isEditing" type="primary" @click="startEditing">
                编辑信息
              </el-button>
              <template v-else>
                <el-button type="primary" @click="saveUserInfo" :loading="isUpdating">
                  保存
                </el-button>
                <el-button @click="cancelEditing"> 取消 </el-button>
              </template>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 修改密码标签页 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="120px"
          >
            <el-form-item label="当前密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>

            <el-form-item label="新密码" prop="password">
              <el-input
                v-model="passwordForm.password"
                type="password"
                show-password
                placeholder="请输入新密码"
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="password1">
              <el-input
                v-model="passwordForm.password1"
                type="password"
                show-password
                placeholder="请再次输入新密码"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="isChangingPassword">
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { UserFilled, Upload, ArrowLeft } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/userStore'
import request from '../utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()
// 获取用户存储
const userStore = useUserStore()

// 标签页状态
const activeTab = ref('info')

// 编辑状态
const isEditing = ref(false)
const isUpdating = ref(false)
const isChangingPassword = ref(false)

// 表单引用
const userFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 用户信息表单
const userForm = reactive({
  username: '',
  realName: '',
  role: '',
  region: '',
  phone: '',
  email: '',
})

// 用户信息表单校验规则
const userFormRules = reactive<FormRules>({
  realName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }],
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  password: '',
  password1: '',
})

// 密码校验函数
const validatePassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6个字符'))
  } else {
    callback()
  }
}

// 确认密码校验函数
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 密码表单校验规则
const passwordRules = reactive<FormRules>({
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  password: [{ required: true, trigger: 'blur', validator: validatePassword }],
  password1: [{ required: true, trigger: 'blur', validator: validateConfirmPassword }],
})

// 初始化用户信息
const initUserInfo = () => {
  const currentUser = userStore.currentUser
  if (currentUser) {
    userForm.username = currentUser.username || ''
    userForm.realName = currentUser.name || ''
    userForm.role = currentUser.role || ''
    userForm.region = currentUser.region || ''
    userForm.phone = currentUser.phone || ''
    userForm.email = currentUser.email || ''
  } else {
    console.error('CurrentUser is null in initUserInfo')
    userForm.username = ''
    userForm.realName = ''
    userForm.role = ''
    userForm.region = ''
    userForm.phone = ''
    userForm.email = ''
  }
}

// 保存用户信息
const saveUserInfo = async () => {
  if (!userFormRef.value) return

  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isUpdating.value = true
        const currentUser = userStore.currentUser
        if (!currentUser) {
          ElMessage.error('用户信息不存在')
          return
        }

        // 构建API请求参数
        const updateData = {
          userId: currentUser.id,
          realName: userForm.realName,
          phone: userForm.phone,
          email: userForm.email,
          region: userForm.region,
          password: '', // 更新个人信息时不传密码
          oldPassword: '',
          password1: '',
          spaceSize: 0,
          role: [],
        }

        // 调用更新个人信息API
        const response = await request.post('/admin/user/updateBaseInfo', updateData)

        if (response.code === 200) {
          // 更新本地 store 中的数据
          userStore.updateUserInfo({
            name: userForm.realName,
            region: userForm.region,
            phone: userForm.phone,
            email: userForm.email,
          })
          ElMessage.success('个人信息更新成功')
          isEditing.value = false
        } else {
          ElMessage.error(response.msg || '更新失败')
        }
      } catch (error) {
        console.error('更新个人信息失败:', error)
        ElMessage.error('更新失败，请稍后重试')
      } finally {
        isUpdating.value = false
      }
    }
  })
}

// 开始编辑
const startEditing = () => {
  isEditing.value = true
}

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false
  initUserInfo() // 重置为原始数据
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        isChangingPassword.value = true
        const currentUser = userStore.currentUser
        if (!currentUser) {
          ElMessage.error('用户信息不存在')
          return
        }

        // 构建API请求参数
        const updateData = {
          userId: currentUser.id,
          realName: currentUser.name,
          phone: currentUser.phone || '',
          email: currentUser.email || '',
          region: currentUser.region || '',
          password: passwordForm.password,
          oldPassword: passwordForm.oldPassword,
          password1: passwordForm.password1,
          spaceSize: 0,
          role: [],
        }

        // 调用修改密码API
        const response = await request.put('/admin/user/updatePwd', updateData)

        if (response.code === 200) {
          ElMessage.success('密码修改成功')
          resetPasswordForm()
        } else {
          ElMessage.error(response.msg || '密码修改失败')
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        ElMessage.error('密码修改失败，请稍后重试')
      } finally {
        isChangingPassword.value = false
      }
    }
  })
}

// 重置密码表单
const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

// 组件挂载时初始化
onMounted(() => {
  initUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.back-btn {
  margin-right: 15px;
  font-size: 16px;
  color: #606266;
}

.back-btn:hover {
  color: var(--el-color-primary);
}

.user-avatar {
  margin-right: 15px;
  color: #fff;
}

.avatar-upload-btn {
  margin-left: 15px;
}

:deep(.el-tabs__nav) {
  padding-left: 20px;
}
</style>
