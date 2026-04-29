<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="../assets/单LOGO.png" alt="系统LOGO" class="login-logo" />
        <h1 class="login-title">{{ systemConfigStore.configData.systemName || 'MES管理系统' }}</h1>
        <p class="login-subtitle">制造执行系统</p>
      </div>

      <div class="login-form">
        <!-- Mock模式提示 -->
        <div v-if="isMockMode" class="mock-hint">
          <el-tag type="warning" size="small">演示模式</el-tag>
          <span class="mock-text">账号: admin / 密码: admin123</span>
        </div>

        <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" status-icon>
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              prefix-icon="User"
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" class="login-button" :loading="loading" @click="handleLogin">
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="login-footer">
        <p>
          <span style="vertical-align: middle"
            >© 2025 {{ systemConfigStore.configData.systemName || 'MES管理系统' }} 版权所有</span
          >
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/userStore'
import { useSystemConfigStore } from '../stores/system/systemConfig'
import { MOCK_ENABLED } from '../mock/mockConfig'
import { authService } from '../mock/mockService'
import { getLoginApiPath } from '../utils/auth'

const userStore = useUserStore()
const systemConfigStore = useSystemConfigStore()
const router = useRouter()
const route = useRoute()
const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false,
})
const loading = ref(false)
const loginFormRef = ref<FormInstance>()
const loginBasicAuthRaw = (import.meta.env.VITE_LOGIN_BASIC_AUTH || '').trim()
const loginBasicAuthHeader = loginBasicAuthRaw.startsWith('Basic ')
  ? loginBasicAuthRaw
  : loginBasicAuthRaw
    ? `Basic ${loginBasicAuthRaw}`
    : ''

const resolveRedirectPath = (): string => {
  const redirect = route.query.redirect
  if (typeof redirect === 'string' && redirect.startsWith('/')) {
    return redirect
  }
  return '/'
}

// 是否为Mock模式
const isMockMode = computed(() => MOCK_ENABLED)

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
  ],
}

// 登录处理函数
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    const valid = await loginFormRef.value.validate()
    if (valid) {
      loading.value = true
      try {
        if (MOCK_ENABLED) {
          // Mock模式登录
          const response = await authService.login(loginForm.username, loginForm.password)

          if ((response.code === 0 || response.code === 200) && response.data) {
            // 调用userStore的login方法
            await userStore.login(response.data, loginForm.rememberMe)

            // 保存记住我信息
            if (loginForm.rememberMe) {
              localStorage.setItem('remember_me', '1')
              localStorage.setItem('remember_username', loginForm.username)
            } else {
              localStorage.removeItem('remember_me')
              localStorage.removeItem('remember_username')
            }

            ElMessage.success('登录成功')
            window.location.href = resolveRedirectPath()
          } else {
            throw new Error(response.msg || '登录失败')
          }
        } else {
          // 真实API登录 - 保留原有逻辑
          const randomStr =
            Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15)
          const params = new URLSearchParams()
          params.append('username', loginForm.username)
          params.append('password', loginForm.password)
          params.append('grant_type', 'password')
          params.append('scope', 'server')
          params.append('randomStr', randomStr)
          params.append('code', '')

          const loginApiPath = getLoginApiPath()
          if (!loginBasicAuthHeader) {
            throw new Error('未配置 VITE_LOGIN_BASIC_AUTH，请先在 .env 中配置登录鉴权凭据')
          }
          const response = await axios.post(loginApiPath, params, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              Authorization: loginBasicAuthHeader,
            },
          })

          if (response.data && response.data.access_token) {
            await userStore.login(response.data, loginForm.rememberMe)

            if (loginForm.rememberMe) {
              localStorage.setItem('remember_me', '1')
              localStorage.setItem('remember_username', loginForm.username)
            } else {
              localStorage.removeItem('remember_me')
              localStorage.removeItem('remember_username')
            }

            ElMessage.success('登录成功')
            window.location.href = resolveRedirectPath()
          } else {
            throw new Error(response.data?.msg || '登录失败')
          }
        }
      } catch (error: any) {
        console.error('登录失败:', error)
        const message = error.response?.data?.msg || error.message || '登录失败，请检查用户名和密码'
        ElMessage.error(message)
      } finally {
        loading.value = false
      }
    }
  } catch (error) {
    return false
  }
}

// 登录页挂载时回填记住的账号
onMounted(() => {
  const remembered = localStorage.getItem('remember_me') === '1'
  loginForm.rememberMe = remembered
  if (remembered) {
    loginForm.username = localStorage.getItem('remember_username') || ''
  }

  // Mock模式下自动填充演示账号
  if (MOCK_ENABLED && !loginForm.username) {
    loginForm.username = 'admin'
    loginForm.password = 'admin123'
  }

  // 获取系统配置
  if (!systemConfigStore.hasLoaded) {
    systemConfigStore.initialize()
  }
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1e5799 0%, #2989d8 50%, #207cca 100%);
  overflow: hidden;
  position: relative;
}

.login-box {
  width: 420px;
  padding: 40px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  height: 60px;
  margin-bottom: 16px;
}

.login-title {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 8px 0 0 0;
}

.login-form {
  margin-bottom: 24px;
}

.mock-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background-color: #fdf6ec;
  border-radius: 4px;
  margin-bottom: 20px;
}

.mock-text {
  font-size: 12px;
  color: #e6a23c;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
}

.login-footer {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 10px;
}

@media (max-width: 576px) {
  .login-box {
    width: 90%;
    padding: 20px;
  }

  .login-logo {
    height: 40px;
  }

  .login-title {
    font-size: 20px;
  }
}
</style>
