# 原始样例项目 README

本文档保留框架抽象前的来源项目说明，用于追溯历史上下文。当前公开框架定位、启动方式和 Agent 协作约束以根目录 `README.md`、`AGENTS.md`、`CLAUDE.md` 为准。

## 来源项目定位

来源项目是一个基于 Vue 3 + TypeScript + Element Plus + Pinia + FastAPI + PostgreSQL 的企业管理系统样例，已包含前端页面、后端接口、权限菜单、基础演示数据以及本地联调所需的核心能力。

在 Universal Fullstack Framework 中，这些能力被抽象为：

- 系统管理基座：组织、账户、角色、菜单权限、系统配置、参数管理、审批规则、日志、备份、消息通知
- 示例业务域 A：主数据、业务单据、状态流转、回款/结算类记录、业务看板
- 示例业务域 B：资源配置、执行记录、结果归档、过程看板
- 本地示例模块：基础 CRUD、项目示例、订单示例、资源示例

前端通过 Vite 启动，开发环境默认代理后端 `http://127.0.0.1:8000`。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Element Plus、Axios、ECharts
- 后端：FastAPI、psycopg、PostgreSQL
- 测试：Vitest、Vue Test Utils、jsdom

## 环境要求

- Node.js `>= 18.18.0`
- npm `>= 8.19.0`
- Python `>= 3.10`
- PostgreSQL `>= 13`

## 快速开始

### 1. 安装前端依赖

```bash
npm install
```

### 2. 准备后端虚拟环境

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

### 3. 配置环境变量

可参考根目录 [`.env.example`](../.env.example) 创建 `.env`。

常用配置如下：

```bash
# 前端
VITE_API_BASE_URL=/api
VITE_DEV_SERVER_URL=http://127.0.0.1:8000
VITE_DEV_LOGIN_API_URL=http://127.0.0.1:8000/auth/oauth2/token

# 后端
APP_ENV=development
APP_PG_HOST=127.0.0.1
APP_PG_PORT=5432
APP_PG_DATABASE=app_local
APP_PG_USER=postgres
APP_PG_PASSWORD=
APP_CORS_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
```

说明：

- 当前项目按 PostgreSQL 模式运行，根目录快捷命令也默认使用 PostgreSQL。
- `APP_*` 是推荐的通用环境变量前缀，后端仍兼容读取历史前缀。
- 线上环境应配置强随机 JWT secret，且正确设置 CORS 白名单。

### 4. 启动后端

推荐在项目根目录直接执行：

```bash
npm run backend:dev
```

或进入 `backend/` 手动启动：

```bash
cd backend
source .venv/bin/activate
python main.py
```

默认地址：

- API：`http://127.0.0.1:8000`
- Swagger：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

### 5. 启动前端

```bash
npm run dev
```

默认地址：

- 前端：`http://127.0.0.1:5174`

## 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 常用命令

### 前端开发

```bash
npm run dev              # 启动开发服务器（0.0.0.0）
npm run dev:local        # 仅本地访问
npm run preview          # 预览构建产物
```

### 后端开发

```bash
npm run backend:dev      # 启动本地后端（PostgreSQL）
npm run backend:dev:pg   # 显式 PostgreSQL 启动
```

### 质量检查

```bash
npm run type-check       # TypeScript 类型检查
npm run lint             # ESLint 自动修复
npm run format           # Prettier 格式化 src/
```

### 测试与构建

```bash
npm run test:unit        # 运行 Vitest
npm run build            # 类型检查 + 构建
npm run build-only       # 仅构建
```

## 功能模块说明

### 系统管理

- 组织架构管理
- 账户管理
- 客户管理
- 用户角色管理
- 资源配置管理
- 参数与编码规则
- 审批规则
- 系统日志、用户日志、备份
- 系统基础配置
- 消息通知
- 个人中心

### 示例业务域 A

- 主数据管理
- 业务单据管理
- 状态流转记录
- 结算类记录
- 业务看板

### 示例业务域 B

- 执行记录管理
- 过程记录
- 结果归档
- 过程看板

### 本地示例

- 本地基础 CRUD
- 项目管理示例
- 订单示例
- 资源示例

## 目录结构

```text
.
├── backend/                # FastAPI 后端
├── docs/                   # 补充文档
├── public/                 # 静态资源
├── scripts/                # 辅助脚本
├── src/
│   ├── api/                # 前端 API 封装
│   ├── components/         # 通用组件
│   ├── config/             # 菜单与框架配置
│   ├── layouts/            # 布局组件
│   ├── router/             # 路由与守卫
│   ├── stores/             # Pinia 状态管理
│   ├── styles/             # 公共样式
│   ├── types/              # TypeScript 类型
│   ├── utils/              # 请求、常量、工具函数
│   └── views/              # 页面视图
├── .env.example            # 环境变量示例
├── AGENTS.md               # AI 协作约束
├── CLAUDE.md               # 额外开发说明
└── package.json            # 前端脚本
```

## 开发约定

- 所有 ID 字段统一使用 `string`
- API 成功码兼容 `0` 和 `200`
- 普通分页默认 `10` 条，选择器场景通常使用 `1000` 条
- 新页面样式需引入 `@/styles/common.css`
- 新增业务页面时，需要同步检查：
  - `src/router/index.ts`
  - `src/config/menuConfig.ts`
  - 后端菜单树与权限
  - 布局菜单过滤逻辑

## 联调与验收建议

每次新增或修改模块，至少执行以下检查：

- 后端：`python3 -m py_compile backend/main.py`
- 前端：`npm run type-check`
- 联调：检查菜单可见、页面可达、按钮可用、接口返回正常
- 业务链路：至少走通一条创建到结果回写的完整流程

## 相关文档

- [AGENTS.md](../AGENTS.md)
- [CLAUDE.md](../CLAUDE.md)
- [backend/README.md](../backend/README.md)
- [FRAMEWORK_GUIDE.md](../FRAMEWORK_GUIDE.md)
