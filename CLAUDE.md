# CLAUDE.md

本文件为 Claude Code 在此代码仓库中工作时提供项目上下文和开发约束。

## 项目定位

Universal Fullstack Framework 是一套面向企业管理系统的可复用全栈开发框架。仓库包含 Vue 3 + TypeScript 前端、FastAPI + PostgreSQL 后端、系统管理基座、示例业务域、本地 CRUD 演示、模块脚手架、registry 接线机制和 baseline 验证链路。

框架核心能力包括：

- 登录、认证、JWT access/refresh token
- 用户、角色、菜单、权限、组织、系统配置
- 日志、备份、消息通知、基础 CRUD
- 前端路由、菜单、布局、权限守卫
- 后端 router/service/repository 分层
- 前端、后端、全栈模块脚手架
- Agent Skill：`skills/universal-fullstack-framework/SKILL.md`

仓库中出现的 `sales`、`production` 等目录和路由前缀是示例业务分组，用来展示模块扩展模式。实际业务项目可以替换为自己的业务域。

## 常用命令

### 开发

```bash
npm run dev              # 启动前端开发服务器
npm run dev:local        # 仅本机访问的前端开发服务器
npm run backend:dev      # 启动 FastAPI 后端
npm run backend:dev:pg   # 显式 PostgreSQL 后端启动
npm run preview          # 预览构建产物
```

### 质量检查

```bash
npm run type-check       # Vue TypeScript 检查
npm run lint             # ESLint 检查并自动修复
npm run format           # Prettier 格式化 src/
npm run build            # 类型检查 + 构建
npm run build-only       # 仅构建
```

### 测试与基座验证

```bash
npm run test:unit
vitest run <file>
vitest run -t "test name"
bash scripts/verify_framework_baseline.sh
```

`scripts/verify_framework_baseline.sh` 是框架级默认验收入口，覆盖 Python 编译、后端回归、HTTP smoke、前端类型检查和构建检查。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Element Plus、Pinia、Vue Router、Axios
- 后端：Python、FastAPI、psycopg、PostgreSQL
- 测试：Vitest、Vue Test Utils、unittest
- 工程化：脚手架、registry、baseline verify、GitHub Actions 示例

## 关键目录

```text
backend/
├── app/modules/                         # 后端模块
├── app/bootstrap/                       # 后端 router registry
├── docs/backend-module-template.md
├── scripts/scaffold_backend_module.py
└── tests/

src/
├── api/                                 # 前端 API 封装
├── config/                              # 菜单、框架配置、scaffold registry
├── layouts/                             # 布局
├── router/                              # 路由与守卫
├── stores/                              # Pinia store
├── styles/                              # 公共样式
├── types/                               # TypeScript 类型
├── utils/                               # request、常量、工具函数
└── views/                               # 页面视图

scripts/
├── scaffold_frontend_module.py
├── scaffold_fullstack_module.py
└── verify_framework_baseline.sh
```

## 框架边界

改动时优先保护这些共享基础设施：

- `src/utils/request.ts`
- `src/router/index.ts`
- `src/config/frameworkConfig.ts`
- `src/config/menuConfig.ts`
- `src/config/scaffoldMenuRegistry.ts`
- `src/router/scaffoldedRoutes.ts`
- `src/layouts/MainLayout.vue`
- `backend/app/bootstrap/router_registry.py`
- `backend/app/bootstrap/scaffold_router_registry.py`
- `backend/app/modules/system_admin/menu.py`
- `backend/app/modules/system_admin/scaffold_menu_registry.py`
- `scripts/verify_framework_baseline.sh`

新增模块优先写入 registry，保持主聚合文件稳定。涉及路由、菜单、权限、布局、后端菜单树的改动必须一起检查。

## 模块脚手架

### 全栈模块

新增标准 CRUD 模块时优先使用全栈脚手架：

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py example_record \
  --tag "示例记录" \
  --api-base-path /manage/api/exampleRecord \
  --table-name example_records \
  --menu-parent system \
  --route-path /system/example-record \
  --route-name system-example-record \
  --function-code APP-FUNC-EXAMPLE-RECORD \
  --with-store
```

生成后立即替换：

- 默认字段：`name/code/status/remark`
- 页面标题、查询项、表格列、表单项、校验规则
- 后端 SQL、表名、字段映射、错误文案
- 菜单标题、图标、权限码语义

### 单边模块

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py <module_name>
./backend/.venv/bin/python scripts/scaffold_frontend_module.py <module_name>
```

仅后端或仅前端任务使用单边脚手架。

## 路由、菜单、权限联动

新增页面或调整路径时同步检查：

1. 前端路由：`src/router/scaffoldedRoutes.ts` 或 `src/router/index.ts`
2. 前端菜单：`src/config/scaffoldMenuRegistry.ts` 或 `src/config/menuConfig.ts`
3. 后端菜单：`backend/app/modules/system_admin/scaffold_menu_registry.py` 或 `backend/app/modules/system_admin/menu.py`
4. 后端 router：`backend/app/bootstrap/scaffold_router_registry.py`
5. 框架开关：`src/config/frameworkConfig.ts`
6. 布局过滤：`src/layouts/MainLayout.vue`
7. 权限码：前端 `meta.functionCode` 与后端 `permission`

访问链路：

1. 登录接口返回 token
2. `userStore` 恢复用户和角色
3. `menuStore` 拉取菜单树和角色授权
4. `MainLayout` 渲染导航
5. `router.beforeEach` 执行认证与权限守卫
6. 页面加载 API 数据

## 前端约定

- 使用 `<script setup lang="ts">` 和 Composition API。
- 使用 `@/` 别名导入本地源码。
- 结构化数据优先用 `interface`。
- ID 字段保持 `string` 语义。
- API 成功响应兼容 `code === 0` 和 `code === 200`。
- 异步操作包含 loading、try/catch/finally 和用户提示。
- 页面样式复用 `@/styles/common.css`、`FormDialog`、`BaseDialog` 等公共能力。
- Store 优先使用 Pinia Composition-style 写法。

标准响应：

```typescript
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}
```

## 后端约定

后端模块保持分层：

```text
backend/app/modules/<domain>/
├── router.py
├── deps.py
├── helpers.py
├── serializers.py
├── routes/
├── services/
└── repositories/
```

职责划分：

- `router.py`：创建和注册 router
- `deps.py`：路由依赖
- `helpers.py`：输入解析与规范化
- `serializers.py`：数据库行到 API 响应的映射
- `routes/`：读取 HTTP 输入并调用服务层
- `services/`：业务编排和事务
- `repositories/`：SQL 与持久化

统一返回：

```json
{ "code": 0, "msg": "success", "data": {} }
```

## 验收清单

框架或模块改动完成后，按影响面运行：

```bash
python3 -m py_compile backend/main.py
npm run type-check
npm run build-only
bash scripts/verify_framework_baseline.sh
```

后端变更需要补跑目标单测。脚手架或 registry 变更需要跑对应 scaffold、menu registry、router registry 测试。

手工 smoke 建议：

1. 登录
2. 访问用户信息接口
3. 打开菜单树
4. 打开一个列表页
5. 执行一个 CRUD 流程

## 参考文档

- `AGENTS.md`
- `README.md`
- `FRAMEWORK_GUIDE.md`
- `docs/fullstack-module-template.md`
- `docs/frontend-module-template.md`
- `backend/docs/backend-module-template.md`
- `docs/ci-baseline.md`
- `skills/universal-fullstack-framework/SKILL.md`
