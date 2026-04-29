# 部门管理和系统配置模块使用示例

## 概述

本文档提供了部门管理和系统配置模块的详细使用示例，包括组件集成、API调用、状态管理等。

## 目录结构

```
system-admin-module/
├── pages/
│   ├── DeptManagement.vue      # 部门管理页面
│   └── SystemConfigView.vue    # 系统配置页面
├── stores/modules/
│   ├── dept.ts                 # 部门管理状态
│   └── systemConfig.ts         # 系统配置状态
├── api/
│   ├── dept.ts                 # 部门管理API
│   └── systemConfig.ts         # 系统配置API
├── types/
│   ├── dept.ts                 # 部门管理类型
│   └── systemConfig.ts         # 系统配置类型
└── router/
    └── systemAdmin.ts          # 路由配置
```

## 1. 部门管理模块

### 1.1 基本使用

```vue
<template>
  <div>
    <!-- 部门管理组件 -->
    <DeptManagement />
  </div>
</template>

<script setup lang="ts">
import DeptManagement from '../pages/DeptManagement.vue'
</script>
```

### 1.2 Store 使用示例

```typescript
import { useDeptStore } from '../stores/modules/dept'

// 在组件中使用
export default {
  setup() {
    const deptStore = useDeptStore()

    // 获取部门树
    const loadDeptTree = async () => {
      await deptStore.fetchDeptTree()
      console.log('部门树:', deptStore.deptTree)
    }

    // 添加部门
    const addNewDept = async () => {
      const deptData = {
        name: '新部门',
        parentId: '0',
        sortOrder: 1,
        enabled: 0
      }
      const userIdList = ['1', '2'] // 部门成员ID列表
      
      const success = await deptStore.addDept(deptData, userIdList)
      if (success) {
        console.log('部门添加成功')
      }
    }

    // 编辑部门
    const editDept = async (deptId: string) => {
      const deptData = {
        deptId,
        name: '编辑后的部门名称',
        sortOrder: 2
      }
      
      const success = await deptStore.updateDept(deptData)
      if (success) {
        console.log('部门更新成功')
      }
    }

    // 删除部门
    const deleteDept = async (deptId: string) => {
      const success = await deptStore.deleteDept(deptId)
      if (success) {
        console.log('部门删除成功')
      }
    }

    return {
      deptStore,
      loadDeptTree,
      addNewDept,
      editDept,
      deleteDept
    }
  }
}
```

### 1.3 API 直接调用示例

```typescript
import { 
  getDeptTreeApi,
  addDeptApi,
  updateDeptApi,
  deleteDeptApi 
} from '../api/dept'

// 获取部门树
const fetchDeptTree = async () => {
  try {
    const response = await getDeptTreeApi()
    if (response.code === 200) {
      console.log('部门树数据:', response.data)
    }
  } catch (error) {
    console.error('获取部门树失败:', error)
  }
}

// 添加部门
const createDept = async () => {
  const deptData = {
    name: '研发部',
    parentId: '0',
    sortOrder: 1,
    enabled: 0
  }
  
  try {
    const response = await addDeptApi(deptData, ['1', '2'])
    if (response.code === 200) {
      console.log('部门创建成功')
    }
  } catch (error) {
    console.error('部门创建失败:', error)
  }
}
```

### 1.4 类型定义使用

```typescript
import type { 
  SysDept, 
  DeptTreeNode, 
  DeptSaveRequest 
} from '../types/dept'

// 定义部门数据
const deptInfo: SysDept = {
  deptId: '1',
  name: '技术部',
  sortOrder: 1,
  parentId: '0',
  enabled: 0
}

// 定义树节点
const treeNode: DeptTreeNode = {
  id: '1',
  name: '技术部',
  parentId: '0',
  type: 0,
  children: []
}

// 定义保存请求
const saveRequest: DeptSaveRequest = {
  sysDept: deptInfo,
  userIdList: ['1', '2', '3']
}
```

## 2. 系统配置模块

### 2.1 基本使用

```vue
<template>
  <div>
    <!-- 系统配置组件 -->
    <SystemConfigView />
  </div>
</template>

<script setup lang="ts">
import SystemConfigView from '../pages/SystemConfigView.vue'
</script>
```

### 2.2 Store 使用示例

```typescript
import { useSystemConfigStore } from '../stores/modules/systemConfig'

export default {
  setup() {
    const systemConfigStore = useSystemConfigStore()

    // 初始化配置
    const initConfig = async () => {
      await systemConfigStore.initialize()
      console.log('系统配置:', systemConfigStore.configData)
    }

    // 更新单个配置
    const updateSingleConfig = async () => {
      const success = await systemConfigStore.updateSystemConfig(
        'companyName', 
        '新公司名称'
      )
      if (success) {
        console.log('配置更新成功')
      }
    }

    // 批量更新配置
    const updateAllConfigs = async () => {
      const configs = {
        companyName: '新公司名称',
        systemName: '新系统名称',
        version: '2.0.0'
      }
      
      const success = await systemConfigStore.updateAllConfigs(configs)
      if (success) {
        console.log('批量更新成功')
      }
    }

    return {
      systemConfigStore,
      initConfig,
      updateSingleConfig,
      updateAllConfigs
    }
  }
}
```

### 2.3 API 直接调用示例

```typescript
import { 
  getSystemConfigApi,
  updateSystemConfigApi,
  updateAllConfigsApi 
} from '../api/systemConfig'

// 获取系统配置
const fetchSystemConfig = async () => {
  try {
    const response = await getSystemConfigApi()
    if (response.code === 200) {
      console.log('系统配置:', response.data)
    }
  } catch (error) {
    console.error('获取系统配置失败:', error)
  }
}

// 更新配置
const updateConfig = async () => {
  const payload = {
    id: 0,
    code: 'systemName',
    value: '新系统名称'
  }
  
  try {
    const response = await updateSystemConfigApi(payload)
    if (response.code === 200) {
      console.log('配置更新成功')
    }
  } catch (error) {
    console.error('配置更新失败:', error)
  }
}
```

### 2.4 类型定义使用

```typescript
import type { 
  SystemConfigData, 
  UpdateConfigRequest,
  ConfigCode 
} from '../types/systemConfig'

// 定义配置数据
const configData: SystemConfigData = {
  companyName: '示例公司',
  systemName: 'GK-CRM系统',
  version: '1.0.0'
}

// 定义更新请求
const updateRequest: UpdateConfigRequest = {
  id: 0,
  code: 'companyName',
  value: '新公司名称'
}

// 使用配置代码常量
const configCode: ConfigCode = 'systemName'
```

## 3. 路由集成

### 3.1 在主应用中集成路由

```typescript
// main.ts 或 router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { systemAdminRoutes } from './system-admin-module/router/systemAdmin'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 其他路由...
    ...systemAdminRoutes,
    // 或者作为子路由
    {
      path: '/admin',
      children: systemAdminRoutes
    }
  ]
})
```

### 3.2 菜单配置

```typescript
import { systemAdminMenus } from './system-admin-module/router/systemAdmin'

// 在菜单配置中使用
const menuConfig = [
  // 其他菜单...
  {
    title: '系统管理',
    children: systemAdminMenus
  }
]
```

## 4. 权限控制

### 4.1 路由守卫

```typescript
import { hasMenuPermission } from './system-admin-module/permissions'

router.beforeEach((to, from, next) => {
  const userRoles = getUserRoles() // 获取用户角色
  
  if (hasMenuPermission(userRoles, to.path)) {
    next()
  } else {
    next('/403') // 无权限页面
  }
})
```

### 4.2 组件中的权限控制

```vue
<template>
  <div>
    <!-- 只有超级管理员可见 -->
    <el-button 
      v-if="hasPermission(['admin'])" 
      @click="handleDelete"
    >
      删除
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { hasButtonPermission } from './system-admin-module/permissions'

const hasPermission = (roles: string[]) => {
  const userRoles = getUserRoles()
  return hasButtonPermission(userRoles, roles)
}
</script>
```

## 5. 完整集成示例

### 5.1 主应用集成

```typescript
// main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// 导入系统管理模块
import { systemAdminRoutes } from './system-admin-module/router/systemAdmin'
import { useDeptStore, useSystemConfigStore } from './system-admin-module/stores'

const app = createApp(App)
const pinia = createPinia()

// 路由配置
const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 主应用路由...
    ...systemAdminRoutes
  ]
})

app.use(pinia)
app.use(router)

// 初始化系统配置
const systemConfigStore = useSystemConfigStore()
systemConfigStore.initialize()

app.mount('#app')
```

### 5.2 在现有页面中使用

```vue
<template>
  <div class="admin-layout">
    <el-container>
      <el-aside width="200px">
        <el-menu>
          <el-menu-item index="/dept-management">
            <el-icon><OfficeBuilding /></el-icon>
            <span>部门管理</span>
          </el-menu-item>
          <el-menu-item index="/system-config">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { OfficeBuilding, Setting } from '@element-plus/icons-vue'
</script>
```

## 6. 错误处理和调试

### 6.1 错误处理

```typescript
import { useDeptStore } from './stores/modules/dept'

const deptStore = useDeptStore()

// 带错误处理的操作
const handleDeptOperation = async () => {
  try {
    deptStore.loading = true
    await deptStore.fetchDeptTree()
  } catch (error) {
    console.error('部门操作失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    deptStore.loading = false
  }
}
```

### 6.2 调试技巧

```typescript
// 开启调试模式
if (process.env.NODE_ENV === 'development') {
  // 监听 store 变化
  deptStore.$subscribe((mutation, state) => {
    console.log('部门 store 变化:', mutation, state)
  })
  
  // 全局错误处理
  window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的 Promise 错误:', event.reason)
  })
}
```

## 7. 性能优化

### 7.1 懒加载

```typescript
// 路由懒加载
const DeptManagement = () => import('../pages/DeptManagement.vue')
const SystemConfigView = () => import('../pages/SystemConfigView.vue')
```

### 7.2 缓存优化

```typescript
// 在 systemConfig store 中已实现 localStorage 缓存
const systemConfigStore = useSystemConfigStore()

// 优先从缓存加载，后台同步最新数据
await systemConfigStore.initialize()
```

## 8. 测试示例

### 8.1 单元测试

```typescript
import { describe, it, expect, vi } from 'vitest'
import { useDeptStore } from '../stores/modules/dept'

describe('部门管理 Store', () => {
  it('应该正确获取部门树', async () => {
    const deptStore = useDeptStore()
    
    // Mock API 响应
    vi.mock('../api/dept', () => ({
      getDeptTreeApi: vi.fn().mockResolvedValue({
        code: 200,
        data: [{ id: '1', name: '测试部门' }]
      })
    }))
    
    await deptStore.fetchDeptTree()
    
    expect(deptStore.deptTree).toHaveLength(1)
    expect(deptStore.deptTree[0].name).toBe('测试部门')
  })
})
```

### 8.2 集成测试

```typescript
import { mount } from '@vue/test-utils'
import DeptManagement from '../pages/DeptManagement.vue'

describe('部门管理页面', () => {
  it('应该正确渲染部门树', async () => {
    const wrapper = mount(DeptManagement)
    
    // 等待数据加载
    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('.dept-tree').exists()).toBe(true)
  })
})
```

## 总结

本模块提供了完整的部门管理和系统配置功能，包括：

1. **完整的 CRUD 操作**：支持部门和配置的增删改查
2. **类型安全**：完整的 TypeScript 类型定义
3. **状态管理**：基于 Pinia 的响应式状态管理
4. **权限控制**：细粒度的权限控制机制
5. **错误处理**：完善的错误处理和用户提示
6. **性能优化**：懒加载、缓存等优化措施

通过以上示例，您可以快速集成和使用这些功能模块。
