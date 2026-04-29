# CLAUDE.md

本文件为Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

这是一个**MES(制造执行系统)管理系统**,使用Vue 3、TypeScript、Element Plus和Pinia构建。这是一个全面的企业级应用程序,用于管理生产任务、计划排程、工艺技术、生产执行、质量监督等制造业务流程。

## 常用命令

### 开发

```bash
# 启动开发服务器
npm run dev

# 本地启动开发服务器(不使用 --host 0.0.0.0)
npm run dev:local

# 生产构建
npm run build

# 预览生产构建
npm run preview

# 运行单元测试
npm run test:unit

# 启动后端（默认 PostgreSQL）
npm run backend:dev

# 显式 PostgreSQL 启动
npm run backend:dev:pg
```

### 代码质量

```bash
# 类型检查
npm run type-check

# ESLint(自动修复)
npm run lint

# 使用Prettier格式化代码
npm run format
```

### 构建过程

构建过程并行运行类型检查和构建:

- `npm run build` = 并发运行`type-check`和`build-only`
- 输出到`dist/`目录

## 架构概述

### 技术栈

- **前端**: Vue 3 + TypeScript + Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **后端**: FastAPI + PostgreSQL

### 核心目录

- `src/views/` - 页面级组件(待实现业务视图)
- `src/components/` - 可复用组件
  - `components/icons/` - 图标组件
  - `components/common/` - 通用组件
- `src/stores/` - Pinia状态管理stores
  - `userStore.ts` - 用户认证与信息管理
  - `userManagementStore.ts` - 用户管理功能
  - `paramConfig.ts` - 系统参数配置
- `src/layouts/` - 布局组件
  - `BaseLayout.vue` - 通用基础布局
  - `MainLayout.vue` - 主应用布局
- `src/utils/` - 工具函数和常量
- `src/types/` - TypeScript类型定义
- `src/router/` - 路由配置

### 核心功能模块(待实现)

根据MES需求规格书,系统将包含以下核心模块:

1. **用户登录** - 用户认证与权限管理
2. **任务管理** - 生产任务的录入与管理
3. **计划排程管理** - 生产计划的排程与调度
4. **工艺技术管理** - 工艺文件与技术文档管理
5. **生产执行管理** - 现场生产过程管理与监控
6. **质量监督管理** - 质量检验、问题处理与追溯
7. **信息发布与展示看板** - 生产数据可视化展示
8. **生产协作** - 跨部门协作与沟通
9. **总体任务执行综合展示** - 任务执行综合看板
10. **系统管理(后台)** - 用户、角色、权限等系统配置

### 系统角色

系统支持以下角色:

| 序号 | 角色名称   | 主要职责                       |
| ---- | ---------- | ------------------------------ |
| 1    | 任务录入员 | 负责生产任务的录入与初步核查   |
| 2    | 计划员     | 负责生产计划的排程、调整与监控 |
| 3    | 工艺技术员 | 负责产品工艺文件的上传与管理   |
| 4    | 生产操作工 | 负责现场生产操作、报工与记录   |
| 5    | 生产管理员 | 负责生产过程的监控与协调       |
| 6    | 质量检验员 | 负责各类质量检验工作           |
| 7    | 质量工程师 | 负责质量问题分析与处理         |
| 8    | 质量负责人 | 负责质量决策与放行审批         |
| 9    | 售后工程师 | 负责现场售后服务与技术支持     |
| 10   | 部门领导   | 负责关键业务审批与决策         |
| 11   | 系统管理员 | 负责系统基础配置与维护         |

## 关键架构模式

### 全局常量管理

页面大小常量集中管理在`src/utils/constants.ts`中:

```typescript
export const PAGE_SIZE_CONFIG = {
  LARGE_PAGE_SIZE: 100000, // 用于大数据量查询
  DEFAULT_PAGE_SIZE: 20, // 默认分页大小
  SMALL_PAGE_SIZE: 10, // 小型列表
} as const
```

**使用方式**: 从`@/utils/constants`导入常量,而不是硬编码数值。

### API响应模式

所有API调用使用标准化响应处理:

```typescript
interface ApiResponse<T> {
  code: number // 0 = 成功
  msg: string
  data: T
}
```

### 基础布局系统

#### BaseLayout组件

`src/layouts/BaseLayout.vue` 提供通用布局功能:

**特性:**

- 响应式顶部导航栏
- 可折叠侧边栏(桌面端)
- 移动端抽屉菜单
- 用户下拉菜单
- 全屏切换
- 插槽化菜单配置

**使用示例:**

```vue
<BaseLayout system-title="MES管理系统">
  <template #header-actions>
    <!-- 自定义头部操作按钮 -->
  </template>

  <template #menu-items>
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <template #title>首页</template>
    </el-menu-item>
  </template>
</BaseLayout>
```

### Store模式

每个store遵循一致的模式:

- 使用Pinia进行响应式状态管理
- 带有加载状态的异步数据获取
- 错误处理和数据验证
- Token管理和权限控制

### 工具函数库

#### 请求封装 (request.ts)

- 支持请求队列和优先级管理
- 自动Token注入
- 统一错误处理
- 401/424状态自动跳转登录

#### 日期工具 (dateUtils.ts)

- 日期格式化
- 时区处理
- 日期范围计算

#### 数据缓存 (dataCache.ts)

- 前端数据缓存机制
- 减少重复API请求

#### 请求队列 (requestQueue.ts)

- 请求优先级管理
- 并发控制

## 开发指南

### 使用Stores

- 始终使用store的fetch方法而不是直接API调用
- 发出请求前检查加载状态
- 使用try-catch块优雅处理错误
- 使用computed属性进行派生状态

### API集成

- 使用`src/utils/request.ts`中的`request`工具
- 遵循统一的日期/时间格式化标准
- 始终包含正确的TypeScript接口
- 对ID使用字符串类型(不是数字)

### 组件开发

- 优先使用组合API(Composition API)
- 使用正确的TypeScript类型
- 遵循Element Plus的表单验证模式
- 为异步操作实现正确的加载状态

### 路由开发

- 所有需要认证的路由设置`meta: { requiresAuth: true }`
- 路由守卫已在`src/router/index.ts`中配置
- 支持基于角色的访问控制

## 关键考虑因素

### 性能

- 大型数据集使用`LARGE_PAGE_SIZE`
- 常规列表页面使用`DEFAULT_PAGE_SIZE`进行分页
- 使用懒加载和按需加载优化性能

### 数据流

- Stores处理所有数据获取和状态管理
- 组件专注于展示和用户交互
- 工具处理横切关注点(请求、格式化等)

### 错误处理

- 所有API调用包含全面错误处理
- 通过Element Plus通知提供用户友好的错误消息
- 正确清理资源和事件监听器

### 响应式设计

- 支持桌面端(>=768px)和移动端(<768px)
- 使用Element Plus的响应式工具
- 移动端优先考虑

## 开发流程

### 添加新功能模块

1. **创建页面视图** - 在`src/views/`中创建Vue组件
2. **创建Store** - 在`src/stores/`中创建Pinia store
3. **配置路由** - 在`src/router/index.ts`中添加路由
4. **添加菜单项** - 在MainLayout中添加导航菜单
5. **实现API接口** - 使用`request`工具调用后端API
6. **类型定义** - 在`src/types/`中定义TypeScript类型

### 代码审查检查清单

- [ ] 是否正确使用TypeScript类型
- [ ] 是否处理加载和错误状态
- [ ] 是否遵循命名规范
- [ ] 是否添加必要的注释
- [ ] 是否通过ESLint检查
- [ ] 是否响应式设计友好

## 项目目标

围绕开发MES系统,通过打通计划与生产现场之间的信息断层,实现生产全过程的数字化、透明化与精细化管理。系统旨在:

- 实时采集与监控生产数据
- 消除信息孤岛
- 提升生产效率与设备利用率
- 严格管控产品质量与实现全程追溯
- 精确管理物料与降低损耗
- 为管理决策提供准确的数据支持
- 最终达到降本增效、快速响应、持续改进的运营优化目的

## 参考文档

- MES需求规格书.md - 详细的功能需求文档
- README.md - 项目说明和使用指南

---

在使用此代码库时,优先理解通过stores的数据流,遵循已建立的API集成模式,并与现有的布局和组件标准保持一致。所有新功能应该基于MES需求规格书中的业务需求进行开发。
