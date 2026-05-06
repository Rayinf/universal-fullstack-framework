# Skill 使用说明

本文说明本仓库内置 Agent Skill 的用途、触发方式和推荐工作流。目标读者是需要借助 AI Agent 维护、扩展或重构 Universal Fullstack Framework 的开发者。

## 1. Skill 定位

仓库内置 Skill 位于：

```text
skills/universal-fullstack-framework/SKILL.md
```

它把本仓库的工程经验整理成一套可触发工作流，适合处理以下任务：

1. 根据需规或手动配置启动一个具体项目。
2. 把存量企业管理系统收敛为可复用全栈框架。
3. 新增标准 CRUD 或业务模块。
4. 对齐前端路由、菜单、权限码和后端菜单树。
5. 对齐前端 API 调用与后端 FastAPI endpoint。
6. 把远程接口、临时 mock 或散落逻辑迁移到本地 FastAPI + PostgreSQL。
7. 修复 404、重定向循环、动态 import/HMR 失败、权限错配等联调问题。
8. 加固认证、JWT、CORS 和发布前验证链路。

## 2. 核心原则

使用 Skill 时，Agent 应优先遵循这些原则：

1. 先保护基座：认证、系统管理、菜单权限、请求封装、路由守卫、脚手架和验证脚本保持稳定。
2. 先形成项目配置：项目名、slug、业务域、模块规划和验收标准先结构化落地。
3. 先对齐契约：前端 API、后端路由、请求字段、返回结构、权限码先形成明确映射。
4. 优先使用脚手架：标准模块优先走仓库内置 backend / frontend / fullstack scaffold。
5. 优先写 registry：新增路由、菜单和后端注册优先落到 scaffold registry。
6. 每次闭环验证：共享链路改动优先运行 `bash scripts/verify_framework_baseline.sh`。

项目启动的 manifest schema、需规抽取规则、配置落点和 starter script 约定见 [Project Start Playbook](../skills/universal-fullstack-framework/references/project-start-playbook.md)。

## 3. 推荐触发方式

在支持 Skill 的 Agent 环境中，可以直接提到 Skill 名称：

```text
请使用 universal-fullstack-framework skill，帮我新增一个示例记录全栈模块。
```

也可以描述任务场景触发：

```text
请基于当前框架新增一个完整 CRUD 模块，前后端一起接入，菜单、路由、权限码和后端接口都要对齐，并跑 baseline 验证。
```

## 4. 首次进入仓库的提示词

首次让 Agent 接手仓库时，推荐使用：

```text
请作为这个仓库的工程协作者工作。

先阅读：
1. AGENTS.md
2. CLAUDE.md
3. README.md
4. skills/universal-fullstack-framework/SKILL.md
5. docs/fullstack-module-template.md
6. docs/frontend-module-template.md
7. backend/docs/backend-module-template.md

然后检查：
1. src/config/frameworkConfig.ts
2. src/router/index.ts
3. src/config/scaffoldMenuRegistry.ts
4. src/router/scaffoldedRoutes.ts
5. backend/app/modules/system_admin/menu.py
6. backend/app/modules/system_admin/scaffold_menu_registry.py
7. backend/app/bootstrap/scaffold_router_registry.py
8. scripts/verify_framework_baseline.sh

请先输出当前框架结构、模块接入链路、脚手架机制、registry 机制和验证链路，再开始执行具体任务。
```

## 5. 项目启动提示词模板

### 5.1 需规自动配置模式

适用于已有需求文档、产品说明、会议纪要或用户故事列表的情况。

```text
请使用 universal-fullstack-framework skill，根据我提供的需规启动一个具体项目。

输入资料：
- 这里粘贴需求规格说明、产品 brief、用户故事或会议纪要。

要求：
1. 先从需规中提取 app_name、app_slug、company_name、目标用户、核心痛点、核心模块、路由前缀、最小 CRUD/API 流程和验收标准。
2. 对缺失但会影响配置的字段提出明确问题。
3. 生成 project.manifest.yaml。
4. 生成 docs/requirements.md。
5. 生成 docs/agent-brief.md，供后续 Agent 进入项目时读取。
6. 根据 manifest 更新前端默认系统名、后端 OpenAPI title/description、frameworkConfig.ts 模块规划。
7. 暂不批量生成业务模块骨架，先完成项目名称和模块规划配置。
8. 修改完成后运行必要验证，并汇报修改文件、验证结果和剩余风险。
```

建议 manifest 结构：

```yaml
project:
  app_name: "服务管理系统"
  app_slug: "service_ops"
  company_name: "示例企业"
  description: "面向服务团队的客户、服务请求、知识库和回访管理系统"
  default_route: "/system/basic-crud"

requirements:
  audience:
    - "服务专员"
    - "客服"
    - "管理层"
  pain_points:
    - "客户资料分散"
    - "服务处理进度不可见"
  core_modules:
    - id: "customer"
      title: "客户管理"
      route_prefix: "/customer"
      enabled: true
    - id: "service_request"
      title: "服务请求"
      route_prefix: "/service-request"
      enabled: false
  acceptance:
    - "管理员可配置用户和角色"
    - "客户列表支持新增、编辑、查询、删除"
```

### 5.2 手动输入配置模式

适用于用户已经知道项目名称、业务域和模块规划的情况。

```text
请使用 universal-fullstack-framework skill，按以下手动配置启动项目。

项目配置：
- app_name: 服务管理系统
- app_slug: service_ops
- company_name: 示例企业
- description: 面向服务团队的客户、服务请求、知识库和回访管理系统
- default_route: /system/basic-crud

模块规划：
- system: 系统管理，route_prefix=/system，enabled=true
- customer: 客户管理，route_prefix=/customer，enabled=true
- service_request: 服务请求，route_prefix=/service-request，enabled=false
- knowledge: 知识库，route_prefix=/knowledge，enabled=false

要求：
1. 生成 project.manifest.yaml。
2. 生成 docs/requirements.md 和 docs/agent-brief.md。
3. 更新项目名称相关配置。
4. 更新 src/config/frameworkConfig.ts 的模块规划。
5. 保持认证、系统管理、请求封装、路由守卫和 registry 主链路稳定。
6. 完成后运行 py_compile / type-check 或 baseline 中必要部分。
```

### 5.3 项目启动输出标准

项目启动任务完成后，Agent 应输出：

```text
项目配置：
- app_name:
- app_slug:
- company_name:
- default_route:

需求摘要：
- 目标用户:
- 核心痛点:
- 核心模块:
- 首批启用模块:

生成/修改文件：
- project.manifest.yaml
- docs/requirements.md
- docs/agent-brief.md
- ...

验证：
- command: result

下一步建议：
- 优先生成哪个全栈模块
- 需要人工确认的业务字段
```

## 6. 新增全栈模块提示词模板

标准新增模块推荐使用全栈脚手架：

```text
请使用 universal-fullstack-framework skill，在当前仓库新增一个完整全栈模块。

模块信息：
- module_name: example_record
- tag: 示例记录
- menu_parent: system
- route_path: /system/example-record
- route_name: system-example-record
- function_code: APP-FUNC-EXAMPLE-RECORD
- api_base_path: /manage/api/exampleRecord
- table_name: example_records
- with_store: true

要求：
1. 优先使用 scripts/scaffold_fullstack_module.py。
2. 生成后替换 name/code/status/remark 等占位字段。
3. 确认前端 meta.functionCode 与后端 permission 一致。
4. 确认前端 route registry、前端 menu registry、后端 menu registry、后端 router registry 都已接入。
5. 按影响范围运行 py_compile、后端目标测试、npm run type-check。
6. 涉及共享链路时运行 bash scripts/verify_framework_baseline.sh。
7. 最终汇报修改文件、验证命令、验证结果和剩余风险。
```

对应命令示例：

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

## 7. 单边模块提示词模板

### 7.1 仅后端模块

```text
请使用 universal-fullstack-framework skill，为当前仓库补一个后端模块。

模块信息：
- module_name: example_record
- tag: 示例记录
- resource_path: /manage/api/exampleRecord
- table_name: example_records

要求：
1. 优先使用 backend/scripts/scaffold_backend_module.py。
2. 补真实字段、SQL、序列化逻辑、查询服务和命令服务。
3. 确认 backend/app/bootstrap/scaffold_router_registry.py 已注册 router。
4. 运行对应 py_compile 和后端目标测试。
```

### 7.2 仅前端模块

```text
请使用 universal-fullstack-framework skill，为当前仓库补一个前端 CRUD 模块。

模块信息：
- module_name: example_record
- tag: 示例记录
- api_base_path: /manage/api/exampleRecord
- menu_parent: system
- route_path: /system/example-record
- route_name: system-example-record
- function_code: APP-FUNC-EXAMPLE-RECORD
- with_store: true

要求：
1. 优先使用 scripts/scaffold_frontend_module.py。
2. 确认 src/router/scaffoldedRoutes.ts、src/config/scaffoldMenuRegistry.ts、backend/app/modules/system_admin/scaffold_menu_registry.py 已写入对应项。
3. 替换页面查询、表格、表单、校验、错误文案等占位内容。
4. 运行 npm run type-check。
```

## 8. 联调排障提示词模板

用于菜单缺失、页面跳转异常、接口 404、权限错配等问题：

```text
请使用 universal-fullstack-framework skill，排查当前仓库的前后端联调问题。

现象：
- 这里写具体现象，例如：点击菜单后跳回默认页，或接口返回 404。

请优先检查：
1. src/config/frameworkConfig.ts
2. src/router/index.ts
3. src/router/scaffoldedRoutes.ts
4. src/config/scaffoldMenuRegistry.ts
5. src/layouts/MainLayout.vue
6. src/stores/menuStore.ts
7. backend/app/modules/system_admin/menu.py
8. backend/app/modules/system_admin/scaffold_menu_registry.py
9. backend/app/bootstrap/scaffold_router_registry.py

请重点核查：
1. route path、menu parent、view bucket 是否匹配。
2. 前端 meta.functionCode 与后端 permission 是否一致。
3. 后端菜单树和角色授权是否包含目标 menuId。
4. 前端 API path 与后端 router prefix 是否一致。
5. 目标模块是否已被 frameworkConfig.ts 启用。

修复后请汇报根因、修改文件、验证命令和验证结果。
```

## 9. 验证标准

常用验证命令：

```bash
python3 -m py_compile backend/main.py
./backend/.venv/bin/python -m unittest backend.tests.test_fullstack_scaffold -v
npm run type-check
npm run build-only
bash scripts/verify_framework_baseline.sh
```

共享链路改动建议运行完整 baseline：

```bash
bash scripts/verify_framework_baseline.sh
```

成功标志：

```text
BASELINE_VERIFY_OK
```

## 10. Agent 输出标准

每次任务结束时，要求 Agent 按下面结构汇报：

```text
修改文件：
- backend: ...
- frontend: ...
- docs/config: ...

关键改动：
- ...

验证：
- command: result

剩余风险：
- ...
```

## 11. 配套文档

- [Framework Guide](../FRAMEWORK_GUIDE.md)
- [Fullstack Module Template](fullstack-module-template.md)
- [Frontend Module Template](frontend-module-template.md)
- [Backend Module Template](../backend/docs/backend-module-template.md)
- [CI Baseline](ci-baseline.md)
- [API Contract Playbook](../skills/universal-fullstack-framework/references/api-contract-playbook.md)
- [Project Start Playbook](../skills/universal-fullstack-framework/references/project-start-playbook.md)
- [Frontend Design Standard](../skills/universal-fullstack-framework/references/frontend-design-standard.md)
