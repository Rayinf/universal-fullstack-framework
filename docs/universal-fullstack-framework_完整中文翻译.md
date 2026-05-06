---
name: universal-fullstack-framework
description: 将一个通用业务 Web 系统从项目启动、配置、构建到重构完整收敛为可复用全栈框架（前端 Vue 3 + TypeScript，后端 Python FastAPI），并在框架之上持续扩展业务模块。适用于根据需规或手动配置初始化项目、设置项目名称和业务模块规划、保留核心系统管理能力、把远程/Mock API 替换为本地后端实现、快速生成标准 CRUD 页面、保持前端设计规范一致、对齐路由/菜单/API 契约、修复前后端联调错误（404、重定向循环、import/HMR 失败），以及在生产部署前加固 auth/JWT/CORS。
---

# Universal Fullstack Framework（完整中文翻译）

## 概览

使用该 skill 的目标是：把现有业务系统转成一个可复用、可增量扩展的开发框架，在稳定核心之上持续叠加新模块。

该 skill 也覆盖项目启动阶段：把需规文档或手动项目配置转成框架 manifest、初始模块规划、应用命名、Agent 协作 brief 和验证清单。

优先保证基础盘稳定：认证、系统管理、配置、用户-角色-权限、日志、备份，以及至少一个基线 CRUD 能力。

核心稳定后，沿用同一套工作流，以“小步可回滚”的方式扩展新业务模块，且不破坏共享前端模式。

## 工作流

### 0) 根据需规或手动配置启动项目

当用户从该框架启动一个新系统，或希望把框架重命名、重配为具体项目时，先执行这一步。

支持两种输入模式：

1. 需规自动配置模式
   - 读取需求文档、产品 brief、截图、会议纪要或用户故事列表。
   - 提取：
     - 项目名称
     - app slug
     - 公司或租户名称
     - 目标用户
     - 核心痛点
     - 规划业务模块
     - 模块路由前缀
     - 最小 CRUD/API 流程
     - 验收标准
   - 仅对会阻塞配置生成的缺失值向用户提问。

2. 手动输入配置模式
   - 接收用户显式给出的配置值，例如：
     - `app_name`
     - `app_slug`
     - `company_name`
     - `description`
     - `default_route`
     - `enabled_modules`
     - `planned_modules`
     - 初始模块字段和 API 路径
   - 对次要缺失值使用保守默认值。

项目启动的标准输出：

- `project.manifest.yaml` 或等价结构化 manifest。
- `docs/requirements.md`，记录目标、用户、痛点、模块规划和验收标准。
- `docs/agent-brief.md`，给后续 Agent 提供项目上下文。
- 前端默认系统名与后端 OpenAPI title/description 配置。
- `src/config/frameworkConfig.ts` 中的初始模块启用计划。
- 首次 baseline 运行的验证清单。

当仓库有本地启动脚本时，优先使用脚本：

```bash
./backend/.venv/bin/python scripts/start_project.py --config project.manifest.yaml
```

当启动脚本尚未存在时，先创建或更新 manifest 和文档，再用最小直接修改应用项目名称和模块配置。

manifest schema、需规抽取规则、配置落点和 starter script 约定见：`references/project-start-playbook.md`。

### 1) 冻结范围并保护核心

- 仅保留核心管理能力和一个基线 CRUD 模块。
- 在路由、菜单、导航守卫中禁用或移除无关业务模块。
- 保持单一首页入口，避免出现重复 dashboard/home 菜单。

### 2) 先建立前后端契约

- 盘点 `src/api/**` 下所有前端 API 调用。
- 把每个调用映射到后端路由、HTTP 方法、请求字段。
- 对未实现端点，三选一：
  - 实现该后端端点。
  - 将前端调用重定向到等价已存在端点。
  - 暂时禁用非关键调用点。
- 优先保证契约兼容，避免大规模前端重写。

端点契约模板与命名规范见：`references/api-contract-playbook.md`。

### 3) 用本地 Python 后端替换远程或 Mock 依赖

- 使用 FastAPI 作为本地后端，并采用明确的模块化端点。
- 为管理页面与 CRUD 示例提供 PostgreSQL（或等价关系型数据库）种子数据。
- 统一响应结构：
  - 成功：`{ code: 0|200, msg, data }`
  - 失败：`{ code: 非0, msg, data: null }`
- 为保持前端一致性，ID 字段统一用字符串。

### 4) 建立前端基线模式

- 使用统一 request 封装与集中错误处理。
- 提供一个完整 CRUD 页面模板：列表、搜索、分页、新增、编辑、删除。
- Store 模式保持一致（Pinia 组合式写法）。
- 复用现有系统页面中的 dialog/form/table 模式。

UI 一致性规则见：`references/frontend-design-standard.md`。

### 5) 系统化解决联调故障

- 遇到 404 风暴，先核对端点路径和 prefix 映射。
- 遇到重试洪泛，仅重试网络错误、429、5xx；不要重试固定 4xx。
- 遇到路由守卫循环，核对重定向终止条件和认证状态初始化。
- 遇到动态导入/样式 500，核对文件路径、别名、预处理器依赖。
- 遇到 HMR 失败，先清理语法/import/runtime 错误，再检查 Vite 配置。

### 6) 加固认证与生产配置

- 密码校验必须用哈希（如 PBKDF2），不要明文比较。
- 使用 JWT access + refresh 双令牌，并校验 token 类型。
- 需要时兼容 refresh token 的请求字段：`refresh_token` 和 `refreshToken`。
- CORS 由环境驱动，并在生产环境启用 fail-fast：
  - 强制使用高强度 JWT secret。
  - 生产环境拒绝通配符 CORS。
  - 强制显式 origin 列表或 regex。

### 7) 每次迭代都要验证

至少运行：

```bash
python3 -m py_compile backend/main.py
npm run type-check
npm run build-only
```

- 若仓库存在 `scripts/verify_framework_baseline.sh`，涉及基座改动时优先运行该脚本，而不是每次手动拼命令。
- `scripts/verify_framework_baseline.sh` 应作为以下改动的默认本地闸门：
  - 后端 route/service/repository 改动
  - 脚手架改动
  - registry 改动
  - 前端 router/menu/request/build 改动

每次核心改动后都要跑 smoke 流程：

1. 登录。
2. 访问受保护的用户信息 API。
3. 访问一个管理列表 API。
4. 刷新 token。
5. 打开 CRUD 页面并执行新增/编辑/删除。

### 8) 在框架之上扩展模块

- 新模块按顺序接入：route -> menu -> page scaffold -> API -> store -> type definitions。
- 先做一个最小可用流程（通常是 list+detail 或 list+CRUD）。
- 先复用共享布局和组件，再考虑新增组件变体。
- 扩展代码尽量隔离在模块目录，除非必要，不要改动核心 auth/request/router。
- 每个新模块都要重复同样的 smoke 与构建验证，再进入下一个模块。

### 8A) 当仓库有本地后端脚手架时优先使用

- 若当前仓库包含 `backend/scripts/scaffold_backend_module.py` 和 `backend/app/modules/_template/`，优先用脚手架，不手工复制模块骨架。
- 示例：

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py quality_report \
  --tag "示例记录" \
  --resource-path /manage/api/exampleRecord \
  --table-name example_records
```

- 生成后立即执行：
  - 替换占位路由路径、表名、标签、错误文案为真实业务值。
  - 确认脚手架已在 `backend/app/bootstrap/scaffold_router_registry.py` 注册新 router。
  - 在 `backend/tests/` 增加或更新针对性测试。
  - 对生成模块跑 `py_compile`，再跑针对性测试和全量后端测试。
- 参数说明和生成布局见：`backend/docs/backend-module-template.md`。
- 最终代码不得保留 `/example`、`example_table`、占位 service 逻辑。

### 8B) 当仓库有本地前端脚手架与注册表时优先使用

- 若当前仓库包含 `scripts/scaffold_frontend_module.py` 和 `scaffolds/frontend_module/`，优先用脚手架，不手工复制 `types/api/view/store`。
- 生成的路由和菜单优先写入注册表文件，例如：
  - `src/router/scaffoldedRoutes.ts`
  - `src/config/scaffoldMenuRegistry.ts`
  - `backend/app/modules/system_admin/scaffold_menu_registry.py`
- `src/router/index.ts`、`src/config/menuConfig.ts`、`backend/app/modules/system_admin/menu.py` 保持为稳定聚合层；已有注册表机制时，不要持续往主文件里塞一次性业务配置。
- 示例：

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py example_record \
  --tag "示例记录" \
  --api-base-path /manage/api/exampleRecord \
  --menu-parent system \
  --route-path /system/example-record \
  --route-name system-example-record \
  --function-code APP-FUNC-EXAMPLE-RECORD \
  --with-store
```

- 生成后立即执行：
  - 用真实业务定义替换占位查询字段、表格列、表单项、校验规则、错误文案。
  - 确认 route/menu 注册落在预期模块桶（如 `root/system/service/operations`）。
  - 确认 `backend/app/modules/system_admin/scaffold_menu_registry.py` 同步出现匹配后端菜单项。
  - 前端 `meta.functionCode` 与后端 `permission` 必须同步一致。
  - 若脚手架行为变更，在 `backend/tests/test_frontend_scaffold.py` 增加或更新测试。
  - 运行：`python3 -m py_compile scripts/scaffold_frontend_module.py backend/tests/test_frontend_scaffold.py`、`python3 -m unittest backend.tests.test_frontend_scaffold -v`、`npm run type-check`。
- 参数说明和生成布局见：`docs/frontend-module-template.md`。
- 生成的占位字段（`name/code/status/remark`）不得作为最终业务 schema。

### 8C) 前后端同时改动时，优先用本地全栈脚手架作为默认入口

- 若当前仓库包含 `scripts/scaffold_fullstack_module.py`，当新模块同时需要后端端点和前端页面/菜单/路由接线时，优先用它。
- 示例：

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

- 该脚本定位是“薄编排器”，不是新的模板体系：
  - 复用 `backend/scripts/scaffold_backend_module.py`
  - 复用 `scripts/scaffold_frontend_module.py`
  - 通过现有 registry 写入，不直接往大主文件追加
- 对标准 CRUD 模块优先使用，因为它会自动覆盖：
  - 后端模块生成
  - 后端 router registry
  - 前端 `types/api/view/store`
  - 前端路由 registry
  - 前端菜单 registry
  - 后端菜单 registry
- 仅在明确单边改动或需要非常规输出路径/注册行为时，回退到 8A 或 8B。
- 生成后立即执行：
  - 用真实业务定义替换占位字段、标签、表名、SQL。
  - 确认 `menu_parent`、前端目录、route 路径都属于同一模块桶。
  - 再次确认前端 `meta.functionCode` 与后端 `permission` 完全一致。
  - 运行：`python3 -m py_compile scripts/scaffold_fullstack_module.py backend/tests/test_fullstack_scaffold.py`、`backend/.venv/bin/python -m unittest backend.tests.test_fullstack_scaffold -v`，若生成文件已落库，再跑 `npm run type-check`。
  - 若仓库存在 `scripts/verify_framework_baseline.sh`，且脚手架改动或生成模块触及共享框架接线，收尾前必须跑一遍。
- 参数说明和推荐流程见：`docs/fullstack-module-template.md`。

### 8D) 保持仓库本地校验入口与 CI 对齐

- 若仓库同时有 `.github/workflows/ci.yml` 与 `scripts/verify_framework_baseline.sh`，要保持功能一致。
- 新增基座强制校验步骤时，必须同时更新：
  - 本地 verify 脚本
  - CI
  - 对应文档（如 `docs/ci-baseline.md`）
- 倾向“少而稳”的检查项，而不是大量脆弱 job；目标是可靠基线闸门，不是堆叠基础设施。

## 输出标准

用该 skill 完成任务后，报告至少包含：

- 按 backend/frontend/config 分组的改动文件。
- 已解决错误类别（404、重定向循环、import 500、认证失败等）。
- 验证命令及通过/失败结果。
- 剩余风险与下一步加固计划。

## 近期坑位与防护栏

应用本 skill 时，默认启用以下防护检查：

### A) route-menu-permission-layout 必须联动

当迁移或新增模块路径（如 `/sales/*`、`/production/*`），必须同步更新：

1. 前端路由（`src/router/scaffoldedRoutes.ts` 或 `src/router/index.ts`）
2. 前端菜单（`src/config/scaffoldMenuRegistry.ts` 或 `src/config/menuConfig.ts`）
3. 后端菜单（`backend/app/modules/system_admin/scaffold_menu_registry.py` 或 `backend/app/modules/system_admin/menu.py`）
4. 布局/菜单过滤与路由守卫 allowlist（`src/layouts/MainLayout.vue`、`src/config/frameworkConfig.ts`、菜单 store 辅助逻辑）

漏任意一项，常见现象是“菜单仍在旧分组”或“菜单完全不可见”。

### B) 菜单树变化后验证 role-menu 映射

- 确保 `role_menus` 默认值由最新 `menu_tree()` 扁平 ID 重建。
- 登录后验证两个端点：
  - `/admin/menu/tree`
  - `/admin/menu/tree/{roleId}`
- 若树正确但 UI 异常，先查前端过滤逻辑。

### C) Seed 数据必须端到端成链，不要孤岛

- 在 `init_db()` 中使用“空表才插入”策略。
- 生成完整业务链，确保页面开箱可测：
  - product -> quotation -> contract -> payment -> commission
  - work order -> work report -> work inbound
- 联调场景避免前端单边 mock 补丁。

### D) UI 一致性要收敛到共享样式

- 新模块页面必须引入共享 common styles。
- 表格容器等跨页间距（桌面/移动）应放在 `src/styles/common.css`。
- 关键间距规则不要只留在历史 demo 页。

### E) 环境与依赖健全性检查

- 涉及 `UploadFile`/`Form` 时，确保项目虚拟环境已安装 `python-multipart`。
- 依赖安装要使用项目虚拟环境解释器，避免全局 Python。
- `Address already in use` 视为端口/进程冲突，不应直接判定为代码回归。

### F) 推荐的增量验证动作

除 compile/type/build 外，涉及导航或模块迁移后，增加以下快速检查：

1. 重新登录并硬刷新。
2. 确认顶层菜单分组与访问路径。
3. 每个模块至少打开一个列表页，检查分页与操作按钮。
4. 验证一个导出/下载动作和一个通知跳转路径。

## 最小通用防护栏（必须保留）

这些规则应作为跨项目执行时的高信号默认规则。

### 1. 变更闭环清单

- 任何功能/模块迁移，都按以下顺序核对：
  - route
  - menu
  - permission/function code
  - guard/filter/allowlist
  - API contract 与 UI 入口

### 2. 契约优先实现

- 编码前先定义端点契约：
  - path
  - method
  - request fields
  - response schema
  - error codes
  - compatibility fields
- 优先做后端兼容适配层，避免大规模前端重写。

### 3. 环境一致性

- 在项目运行时环境（venv/workspace）安装和运行依赖，不用全局运行时。
- 遇到缺包类运行时错误，优先核对解释器路径。

### 4. 共享样式治理

- 跨页面样式规则统一收敛到共享样式文件。
- 页面局部样式只保留“有意差异”的部分。

### 5. 迭代闸门（最小要求）

- 未通过以下检查，不进入下一步：
  - `python3 -m py_compile backend/main.py`（或项目等价编译检查）
  - `npm run type-check`（或前端等价类型检查）
  - `npm run build-only`（或项目等价构建）
  - 一条 smoke 流程：登录 + 受保护 API + 一个 CRUD 新增/编辑/删除

---

## 本仓库中“每个脚本”的作用说明

以下脚本来自该 skill 在当前仓库里对应的落地实现：

### 1) `scripts/verify_framework_baseline.sh`

- 作用：一键执行“框架基线”本地闸门检查，避免手动漏项。
- 主要步骤（按脚本顺序）：
  1. Python 编译检查（后端主程序、脚手架脚本、关键测试文件）。
  2. 后端基座回归测试（scaffold、菜单/路由注册等）。
  3. PostgreSQL HTTP smoke 测试。
  4. 前端 `npm run type-check`。
  5. 前端 `npm run build-only`。
- 关键特性：`set -euo pipefail`，任一步失败即退出；支持通过 `PYTHON_BIN` 覆盖解释器路径。

### 2) `backend/scripts/scaffold_backend_module.py`

- 作用：基于后端模板目录快速生成模块化后端骨架（routes/service/repo 等），并可自动写入路由注册表。
- 主要能力：
  - 校验模块名（snake_case）。
  - 基于模板做字符串替换（模块名、类名、路径、表名、tag）。
  - 重命名模板文件（如 `example_routes.py` -> `<module>_routes.py`）。
  - 冲突检测：目标目录已存在或注册项已存在会报错。
  - 自动注册：向 `backend/app/bootstrap/scaffold_router_registry.py` 插入 router 条目。

### 3) `scripts/scaffold_frontend_module.py`

- 作用：基于前端模板一次性生成 `types/api/view/store` 等文件，并自动注册前端路由、前端菜单、后端菜单映射。
- 主要能力：
  - 统一命名转换（snake/camel/pascal/kebab）。
  - 校验菜单桶与路由前缀一致（`root/system/sales/production`）。
  - 维护注册表文件：
    - `src/router/scaffoldedRoutes.ts`
    - `src/config/scaffoldMenuRegistry.ts`
    - `backend/app/modules/system_admin/scaffold_menu_registry.py`
  - 支持 `--with-store` 等参数开关，生成可选 store。
  - 预防重复注册与路径冲突。

### 4) `scripts/scaffold_fullstack_module.py`

- 作用：全栈脚手架总入口；在一个命令里编排后端+前端双侧生成与注册。
- 主要能力：
  - 复用 `scaffold_backend_module.py` 与 `scaffold_frontend_module.py`，不重复造模板体系。
  - 根据 `menu_parent` 自动选择前端目录默认值。
  - 预检查前后端模板和目标冲突，避免半成品落库。
  - 失败回滚：若任何一步异常，会删除已生成文件并恢复注册表快照，保证仓库一致性。
- 适用场景：新模块同时涉及后端端点与前端页面/路由/菜单接线时，优先用它。
