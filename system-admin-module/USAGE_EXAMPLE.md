# 系统管理模块使用示例

## 1. 基本集成示例

### 在主应用中集成系统管理模块

```typescript
// main.ts
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import { systemRoutes } from './system-admin-module'

const app = createApp(App)

// 配置路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    // 集成系统管理路由
    systemRoutes,
    // 其他路由...
  ]
})

// 配置状态管理
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.mount('#app')
```

## 2. 权限控制示例

### 路由守卫配置

```typescript
// router/guards.ts
import { useAuthStore } from './system-admin-module'
import { hasMenuPermission } from './system-admin-module'

export function setupRouterGuards(router: Router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    
    // 检查是否需要登录
    if (to.meta.requiresAuth && !authStore.token) {
      next('/login')
      return
    }
    
    // 检查权限
    if (to.meta.roles) {
      const userRoles = authStore.userInfo?.roles || []
      const hasPermission = to.meta.roles.some((role: string) => 
        userRoles.includes(role)
      )
      
      if (!hasPermission) {
        next('/403')
        return
      }
    }
    
    next()
  })
}
```

### 组件中的权限控制

```vue
<template>
  <div>
    <!-- 只有超级管理员可以看到 -->
    <el-button 
      v-if="isSuperAdmin" 
      type="danger" 
      @click="handleDelete"
    >
      删除用户
    </el-button>
    
    <!-- 根据按钮权限显示 -->
    <el-button 
      v-if="hasButtonPermission(['1'], 'order_create')" 
      type="primary"
    >
      新增订单
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore, hasButtonPermission, isSuperAdmin } from '../system-admin-module'

const authStore = useAuthStore()

const userRoles = computed(() => authStore.userInfo?.roles || [])
const isSuperAdminUser = computed(() => isSuperAdmin(userRoles.value))

const handleDelete = () => {
  // 删除逻辑
}
</script>
```

## 3. API调用示例

### 用户管理API使用

```typescript
// composables/useUserManagement.ts
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  pageUsersApi, 
  createUserApi, 
  updateUserApi, 
  deleteUserApi,
  type UserRecord,
  type UserCreateDto 
} from '../system-admin-module'

export function useUserManagement() {
  const loading = ref(false)
  const users = ref<UserRecord[]>([])
  const total = ref(0)

  // 获取用户列表
  const fetchUsers = async (params: any) => {
    loading.value = true
    try {
      const response = await pageUsersApi(params)
      if (response.code === 200 && response.data) {
        users.value = response.data.records
        total.value = response.data.total
      }
    } catch (error) {
      ElMessage.error('获取用户列表失败')
    } finally {
      loading.value = false
    }
  }

  // 创建用户
  const createUser = async (userData: UserCreateDto) => {
    try {
      const response = await createUserApi(userData)
      if (response.code === 200) {
        ElMessage.success('用户创建成功')
        return true
      }
    } catch (error) {
      ElMessage.error('用户创建失败')
    }
    return false
  }

  // 删除用户
  const deleteUser = async (userId: string) => {
    try {
      const response = await deleteUserApi(userId)
      if (response.code === 200) {
        ElMessage.success('用户删除成功')
        return true
      }
    } catch (error) {
      ElMessage.error('用户删除失败')
    }
    return false
  }

  return {
    loading,
    users,
    total,
    fetchUsers,
    createUser,
    deleteUser
  }
}
```

### 在组件中使用

```vue
<template>
  <div class="user-management">
    <el-table :data="users" v-loading="loading">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="realName" label="真实姓名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserManagement } from '../composables/useUserManagement'

const { loading, users, total, fetchUsers, deleteUser } = useUserManagement()

const currentPage = ref(1)
const pageSize = ref(10)

const handlePageChange = () => {
  fetchUsers({
    current: currentPage.value,
    size: pageSize.value
  })
}

const handleEdit = (user: any) => {
  // 编辑逻辑
}

const handleDelete = async (user: any) => {
  const success = await deleteUser(user.userId)
  if (success) {
    handlePageChange() // 刷新列表
  }
}

onMounted(() => {
  handlePageChange()
})
</script>
```

## 4. 状态管理示例

### 使用认证状态

```vue
<template>
  <div class="header">
    <div class="user-info" v-if="userInfo">
      <el-avatar :src="userInfo.avatar">
        {{ userInfo.name?.charAt(0) }}
      </el-avatar>
      <span>{{ userInfo.name }}</span>
      <el-dropdown @command="handleCommand">
        <el-icon><ArrowDown /></el-icon>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../system-admin-module'

const router = useRouter()
const authStore = useAuthStore()

const userInfo = computed(() => authStore.userInfo)

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/system/profile')
      break
    case 'logout':
      authStore.logout()
      router.push('/login')
      break
  }
}
</script>
```

## 5. 自定义配置示例

### 自定义API基础URL

```typescript
// config/api.ts
import { request } from '../system-admin-module/utils/request'

// 自定义请求实例
export const customRequest = request.create({
  baseURL: 'https://your-api-domain.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 自定义拦截器
customRequest.interceptors.request.use(
  (config) => {
    // 添加自定义请求头
    const token = localStorage.getItem('custom_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)
```

### 自定义权限配置

```typescript
// config/custom-permissions.ts
import { ROLE_IDS, MENU_KEYS } from '../system-admin-module'

// 扩展角色定义
export const CUSTOM_ROLE_IDS = {
  ...ROLE_IDS,
  CUSTOM_ROLE: '10' // 自定义角色
}

// 扩展菜单权限
export const CUSTOM_ROLE_PERMISSIONS = {
  [CUSTOM_ROLE_IDS.CUSTOM_ROLE]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    // 自定义菜单权限
  ]
}
```

## 6. 样式自定义示例

### 覆盖默认样式

```scss
// styles/system-admin-override.scss

// 自定义系统管理页面样式
.system-admin-module {
  .app-page {
    background-color: #f5f5f5;
  }
  
  .page-toolbar {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .table-card {
    .el-card__header {
      background-color: #fafafa;
    }
  }
}

// 自定义对话框样式
.base-dialog {
  .el-dialog__header {
    background-color: #409eff;
    color: white;
  }
}
```

## 7. 错误处理示例

### 全局错误处理

```typescript
// utils/error-handler.ts
import { ElMessage, ElNotification } from 'element-plus'

export function setupErrorHandler() {
  // 全局错误处理
  window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise拒绝:', event.reason)
    ElMessage.error('系统错误，请稍后重试')
  })

  // Vue错误处理
  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue错误:', err, info)
    ElNotification.error({
      title: '系统错误',
      message: '页面出现异常，请刷新页面重试'
    })
  }
}
```

### API错误处理

```typescript
// api/error-handler.ts
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../system-admin-module'

export function handleApiError(error: any) {
  const authStore = useAuthStore()
  
  if (error.response) {
    const { status, data } = error.response
    
    switch (status) {
      case 401:
        ElMessage.error('登录已过期，请重新登录')
        authStore.logout()
        break
      case 403:
        ElMessage.error('权限不足')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error('服务器内部错误')
        break
      default:
        ElMessage.error(data?.msg || '请求失败')
    }
  } else {
    ElMessage.error('网络错误，请检查网络连接')
  }
}
```

这些示例展示了如何在实际项目中集成和使用系统管理模块。根据具体需求，可以进一步自定义和扩展功能。
