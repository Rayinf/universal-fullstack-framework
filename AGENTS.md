# AGENTS.md - AI编程助手指南

本文件为AI编程助手(如Claude、Cursor AI、GitHub Copilot)在此代码库中工作提供指导。

## 1. 项目概述

这是一个**MES(制造执行系统)管理系统**,使用Vue 3、TypeScript、Element Plus和Pinia构建。

**技术栈**: Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus + Axios

## 2. 构建/测试命令

### 开发命令

```bash
npm run dev              # 启动开发服务器 (--host 0.0.0.0)
npm run dev:local        # 本地开发服务器 (仅localhost)
npm run backend:dev      # 启动后端(默认 PostgreSQL)
npm run backend:dev:pg   # 显式启动 PostgreSQL 后端
npm run build            # 生产构建 (并行运行type-check和build-only)
npm run preview          # 预览生产构建
```

### 代码质量命令

```bash
npm run lint             # ESLint检查并自动修复
npm run format           # Prettier格式化代码
npm run type-check       # TypeScript类型检查
```

### 测试命令

```bash
npm run test:unit        # 运行所有单元测试 (使用vitest)
vitest run <文件路径>     # 运行单个测试文件
vitest run -t "测试名称"  # 运行匹配名称的测试
```

**测试配置**: Vitest + jsdom环境 + Vue Test Utils

## 3. 代码风格指南

### 3.1 导入规范

**导入顺序**:

1. Vue核心导入
2. 第三方库 (Element Plus、图标等)
3. 本地类型定义 (`@/types/*`)
4. 本地API (`@/api/*`)
5. 本地Store (`@/stores/*`)
6. 本地组件 (`@/components/*`)
7. 本地工具 (`@/utils/*`)
8. 本地Composables (`@/composables/*`)

```typescript
// ✅ 正确示例
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import type { BasicInfoRecord } from '@/types/parameter'
import { pageBasicInfoApi } from '@/api/parameter'
import { useParameterStore } from '@/stores/parameterStore'
import FormDialog from '@/components/common/FormDialog.vue'
import { formatDate } from '@/utils/dateUtils'
```

**路径别名**: 始终使用 `@/` 代替相对路径 `../`

### 3.2 TypeScript类型规范

**必须明确类型**:

```typescript
// ✅ 正确
const users = ref<User[]>([])
const loading = ref<boolean>(false)
const total = ref<number>(0)

// ❌ 错误 - 避免隐式any
const data = ref([])
```

**接口定义**:

```typescript
// 统一使用interface而非type (除非需要联合类型)
export interface ApiResponse<T> {
  code: number
  msg: string
  data?: T
}
```

**ID类型一致性**: 所有`userId`, `salesId`等ID字段统一使用`string`类型,不使用`number`

### 3.3 命名约定

- **变量/函数**: camelCase (`fetchUsers`, `isLoading`)
- **组件**: PascalCase (`FormDialog.vue`, `BaseDialog.vue`)
- **常量**: UPPER_SNAKE_CASE (`PAGE_SIZE_CONFIG`, `API_BASE_URL`)
- **类型/接口**: PascalCase (`UserRecord`, `ApiResponse`)
- **Store**: camelCase + Store后缀 (`useUserStore`, `useParameterStore`)

### 3.4 Vue组件规范

**使用Composition API** (setup script):

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

// 定义props
interface Props {
  modelValue: boolean
  title: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

// 定义emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [data: Record<string, any>]
}>()
</script>
```

**模板顺序**: `<template>` → `<script setup>` → `<style scoped>`

### 3.5 Pinia Store规范

**使用Composition API风格**:

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useExampleStore = defineStore('example', () => {
  // State
  const data = ref<DataType[]>([])
  const loading = ref(false)

  // Actions
  const fetchData = async () => {
    loading.value = true
    try {
      // API调用
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    fetchData,
  }
})
```

### 3.6 API请求规范

**使用封装的request工具**:

```typescript
import request from '@/utils/request'

// GET请求
const result = await request.get<ResponseType>('/api/path', params)

// POST请求
const result = await request.post<ResponseType>('/api/path', data)
```

**标准响应处理**:

```typescript
if (result.code === 0 || result.code === 200) {
  // 成功处理
  data.value = result.data || []
} else {
  ElMessage.error(result.msg || '操作失败')
}
```

## 4. 错误处理规范

**必须包含完整的错误处理**:

```typescript
const fetchData = async () => {
  loading.value = true
  try {
    const res = await api()
    if (res.code === 0) {
      data.value = res.data || []
    } else {
      ElMessage.error(res.msg || '获取数据失败')
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('发生网络错误')
  } finally {
    loading.value = false
  }
}
```

**关键要点**:

- 所有异步操作必须try-catch
- 失败时重置数据为空状态
- 使用ElMessage显示用户友好的错误消息
- 记录console.error以便调试

## 5. 分页参数管理

**智能分页机制** - 避免页面间参数污染:

```typescript
// 只有在没有传入特定size参数时,才更新本地分页参数
if (!params?.size) {
  currentPage.value = response.data.current
  pageSize.value = response.data.size
}
```

**使用场景**:

- 列表页面: 使用默认`size: 10`
- 下拉选择器: 传入`size: 1000`获取全量数据

## 6. 资源清理

**组件卸载时清理资源**:

```typescript
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  // 清理其他资源
})
```

## 7. 常量管理

**使用集中的常量文件** (`src/utils/constants.ts`):

```typescript
export const PAGE_SIZE_CONFIG = {
  LARGE_PAGE_SIZE: 100000,
  DEFAULT_PAGE_SIZE: 20,
  SMALL_PAGE_SIZE: 10,
} as const
```

**禁止硬编码数值** - 始终从constants导入

## 8. Element Plus使用规范

- 使用`ElMessage`显示提示信息
- 使用`ElMessageBox.confirm`确认危险操作
- 表单验证使用`:rules`属性
- 表格使用`stripe`和`highlight-current-row`属性

## 9. 图表设计规范 (ECharts)

**统一配色方案**:

```javascript
const colors = {
  primary: ['#6366f1', '#818cf8', '#a5b4fc'],
  success: ['#14b8a6', '#5eead4', '#99f6e4'],
  warning: ['#f59e0b', '#fbbf24', '#fcd34d'],
}
```

**必须实现响应式**:

```javascript
onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach((chart) => chart.dispose())
})
```

## 10. 文件组织

```
src/
├── api/          # API接口定义
├── assets/       # 静态资源
├── components/   # 可复用组件
│   ├── common/   # 通用组件
│   └── icons/    # 图标组件
├── layouts/      # 布局组件
├── router/       # 路由配置
├── stores/       # Pinia状态管理
├── types/        # TypeScript类型定义
├── utils/        # 工具函数
└── views/        # 页面组件
```

## 11. Git提交规范

使用约定式提交:

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具变动

## 12. 关键注意事项

1. **始终用中文回复用户** (来自~/.claude/CLAUDE.md)
2. 所有ID字段使用`string`类型
3. API响应code为0或200表示成功
4. 分页默认10条,选择器使用1000条
5. 新建文件时优先编辑现有文件
6. 遵循已有的组件和Store模式
7. Token自动注入,无需手动处理Authorization
8. 后端数据库统一为 PostgreSQL，不再保留旧本地回退库路径

## 13. 近期实战经验（Skill更新）

以下规则来自最近阶段（销售+生产闭环）的真实踩坑，后续开发必须默认遵循。

### 13.1 路由/菜单/权限联动检查（高优先级）

新增或调整页面路径时，必须同步更新以下4处：

1. 前端路由：`src/router/index.ts`
2. 前端菜单配置：`src/config/menuConfig.ts`
3. 后端菜单树：`backend/main.py` 的 `menu_tree()`
4. 布局菜单过滤逻辑：`src/layouts/MainLayout.vue` / `src/config/frameworkConfig.ts`

**关键坑位**：

- 仅改路由和菜单不够，若布局仍写死只显示`/system/*`，新模块（如`/sales/*`、`/production/*`）会被直接过滤，看起来像“菜单没生效”。
- `meta.functionCode` 与后端 `permission` 必须一致，否则会被路由守卫判定无权限并重定向。

### 13.2 菜单权限初始化规则

- `role_menus` 默认权限来源于 `default_menu_ids = flatten_menu_ids(menu_tree())`。
- 调整菜单树结构（如把业务从系统管理拆到独立一级）后，必须确认默认角色仍能拿到新菜单ID。
- 验证顺序：登录后检查 `/admin/menu/tree`、`/admin/menu/tree/{roleId}` 返回值，再看前端渲染。

### 13.3 后端依赖与运行环境

- 涉及 `UploadFile/Form` 的接口，虚拟环境必须安装 `python-multipart`。
- 依赖安装要在项目虚拟环境执行：
  - `./.venv/bin/python -m pip install -r requirements.txt`
- 启动报 `Address already in use` 多为端口占用，不是代码错误；需先确认已有进程。

### 13.4 模拟数据（Seed）规范

- 所有演示数据统一放 `init_db()`，并使用“空表才插入”模式：
  - `SELECT COUNT(1) AS cnt FROM xxx` + `if cnt == 0: seed...`
- 业务链路型数据要成套提供（如：产品→报价→合同→回款→佣金、工单→报工→入库），避免页面可进但无可测数据。
- 不要在前端写死mock，优先走后端初始化数据，保证联调一致性。

### 13.5 页面样式一致性规范

- 新业务页面必须 `@import '@/styles/common.css'`。
- 通用表格容器样式放入 `common.css`（如 `.table-container` 的桌面/移动端内边距），不要只在老页面局部定义。
- 目标：新增页面与示例页在留白、表格密度、分页区视觉上保持一致。

### 13.6 每次阶段开发的最小验收清单

后端：

- `python3 -m py_compile backend/main.py`
- 必要时执行 `init_db()` 并抽查关键表计数

前端：

- `npm run type-check`
- 手工验证：菜单层级、页面可达、按钮可用、导出可下载、通知可跳转

联调：

- 至少走通一条端到端业务链路（创建→审批/流转→结果回写）。

详细架构和业务规则请参考: `CLAUDE.md`
