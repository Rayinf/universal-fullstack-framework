# AI 提示词模板手册

本文提供的是“可直接复制给 AI”的项目内高频提示词模板。  
这些模板不是万能答案，而是帮助同事把任务说清楚，让 AI 更快进入这个仓库的正确上下文。

## 1. 通用原则

每次给 AI 下任务时，尽量包含这 5 类信息：

1. 任务目标
2. 修改边界
3. 模块接入信息
4. 验收标准
5. 必须读取的项目文件

## 2. 首次进入仓库的启动模板

适用场景：

1. 同事第一次让 AI 接手这个项目
2. 切换到一个新的 AI 工具
3. 长时间没做这个仓库，需要重新建立上下文

可直接复制：

```text
你现在要作为这个仓库的工程协作者参与开发。先不要直接写代码。

请先完成以下步骤：
1. 阅读 AGENTS.md、CLAUDE.md。
2. 阅读 docs/training/framework-baseline-training.md、docs/training/skills-training.md、docs/training/scaffold-registry-verify-training.md。
3. 检查 src/config/frameworkConfig.ts、src/router/index.ts、src/config/menuConfig.ts、src/layouts/MainLayout.vue、src/stores/menuStore.ts、backend/main.py、backend/app/modules/system_admin/menu.py、scripts/verify_framework_baseline.sh。
4. 用中文输出当前仓库的实际结构总结，重点说明：
   - 当前启用模块
   - 路由/菜单/权限/后端菜单树联动方式
   - 脚手架和 registry 机制
   - baseline 验证链路
5. 在总结后，再给出你建议我后续如何向你描述任务，才能让你更稳定地继续开发。

注意：
- 以当前代码为准，不要只依赖旧 README。
- 后续开发要优先复用脚手架和 registry，不要随意扩写主文件。
```

## 3. 项目启动模板

适用场景：

1. 从需规或产品说明启动一个具体项目
2. 手动输入项目名称、业务域和模块规划
3. 需要让 Agent 先生成项目配置、需求摘要和协作上下文

### 3.1 需规自动配置

可直接复制：

```text
请使用 universal-fullstack-framework skill，根据下面的需规启动项目。

输入资料：
[粘贴需求规格说明、产品 brief、会议纪要或用户故事]

要求：
1. 先阅读 skills/universal-fullstack-framework/SKILL.md 和 skills/universal-fullstack-framework/references/project-start-playbook.md。
2. 从输入资料中提取 app_name、app_slug、company_name、description、target users、pain points、core modules、route_prefix、acceptance。
3. 对缺失但会阻塞配置的字段提出问题。
4. 生成 project.manifest.yaml。
5. 生成 docs/requirements.md。
6. 生成 docs/agent-brief.md。
7. 根据 manifest 更新项目名称 fallback、后端 OpenAPI title/description、src/config/frameworkConfig.ts。
8. 先完成项目配置，不批量生成业务模块。
9. 运行必要验证，并汇报修改文件、验证结果、open questions 和下一步建议。
```

### 3.2 手动输入配置

可直接复制：

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

要求：
1. 生成 project.manifest.yaml、docs/requirements.md、docs/agent-brief.md。
2. 更新项目名称相关 fallback 和 frameworkConfig.ts 模块规划。
3. 保持认证、系统管理、请求封装、路由守卫和 registry 主链路稳定。
4. 完成后运行 py_compile / type-check 或 baseline 中必要部分。
```

## 4. 新增全栈模块模板

适用场景：

1. 要同时补前端页面和后端接口
2. 要新增标准业务模块

可直接复制：

```text
请在这个仓库里新增一个完整业务模块，并直接完成代码修改。

任务信息：
- 模块名 module_name: quality_report
- 中文标签 tag: 质检报告
- 菜单分组 menu_parent: production
- 路由路径 route_path: /production/quality-report
- 路由名称 route_name: production-quality-report
- 权限码 function_code: SRS-FUNC-QUALITY-REPORT
- 前端 API 前缀 api_base_path: /manage/api/qualityReport
- 后端表名 table_name: quality_report_records
- 需要 store: 是

要求：
1. 先阅读 AGENTS.md、CLAUDE.md、docs/fullstack-module-template.md、docs/training/framework-baseline-training.md、docs/training/scaffold-registry-verify-training.md。
2. 优先使用 scripts/scaffold_fullstack_module.py，不要手工复制旧模块。
3. 生成后立即把占位字段、占位文案、占位 SQL 替换为真实业务定义。
4. 确保前端 meta.functionCode 和后端 permission 完全一致。
5. 确保 route、menu、backend menu、backend router 都正确接入 registry。
6. 修改完成后运行必要验证，并汇报：
   - 修改的文件
   - 运行的命令
   - 通过的验证
   - 剩余风险

注意：
- 中文回复。
- 所有 ID 字段保持 string 语义。
- API 成功响应按 code = 0 或 200 处理。
```

## 5. 只补前端模块模板

适用场景：

1. 后端接口已存在
2. 要快速补前端 CRUD 页面

可直接复制：

```text
请在这个仓库里补一个前端模块，并直接完成代码修改。

任务信息：
- 模块名 module_name: quality_report
- 中文标签 tag: 质检报告
- 菜单分组 menu_parent: production
- 路由路径 route_path: /production/quality-report
- 路由名称 route_name: production-quality-report
- 权限码 function_code: SRS-FUNC-QUALITY-REPORT
- 前端 API 前缀 api_base_path: /manage/api/qualityReport
- 需要 store: 是

要求：
1. 先阅读 AGENTS.md、CLAUDE.md、docs/frontend-module-template.md。
2. 优先使用 scripts/scaffold_frontend_module.py。
3. 确保把新页面写入 src/router/scaffoldedRoutes.ts、src/config/scaffoldMenuRegistry.ts、backend/app/modules/system_admin/scaffold_menu_registry.py。
4. 替换所有脚手架占位字段和占位文案。
5. 检查 frameworkConfig.ts、MainLayout.vue、router/index.ts 的联动影响。
6. 至少运行 npm run type-check，并汇报结果。
```

## 6. 只补后端模块模板

适用场景：

1. 前端已经有页面
2. 后端接口还没实现

可直接复制：

```text
请在这个仓库里补一个后端模块，并直接完成代码修改。

任务信息：
- 模块名 module_name: quality_report
- 中文标签 tag: 质检报告
- 资源路径 resource_path: /manage/api/qualityReport
- 表名 table_name: quality_report_records

要求：
1. 先阅读 AGENTS.md、CLAUDE.md、backend/docs/backend-module-template.md。
2. 优先使用 backend/scripts/scaffold_backend_module.py。
3. 生成后补齐真实 SQL、字段映射、服务层逻辑和错误处理。
4. 确保模块正确写入 backend/app/bootstrap/scaffold_router_registry.py。
5. 如果模块需要出现在导航菜单中，同步检查 backend/app/modules/system_admin/scaffold_menu_registry.py。
6. 至少运行相关 py_compile 和目标测试，并汇报结果。
```

## 7. 排查菜单/权限/路由问题模板

适用场景：

1. 菜单不显示
2. 页面被重定向
3. 权限看起来存在但无法访问

可直接复制：

```text
请帮我排查这个仓库里的路由/菜单/权限联动问题，并在确认原因后直接修复代码。

现象：
- [在这里写具体现象]

要求你优先检查这些文件：
- src/config/frameworkConfig.ts
- src/router/index.ts
- src/config/menuConfig.ts
- src/layouts/MainLayout.vue
- src/stores/menuStore.ts
- backend/app/modules/system_admin/menu.py

请重点核查：
1. 目标路径是否属于已启用模块
2. 前端 meta.functionCode 和后端 permission 是否一致
3. 菜单节点是否真正进入后端菜单树
4. 当前角色是否能拿到对应 menuId
5. 是否因为 fallback 菜单机制掩盖了权限问题

修复后请给我：
- 根因说明
- 修改文件
- 验证方式
- 剩余风险
```

## 8. 基座级代码审查模板

适用场景：

1. review 同事改动
2. review AI 自己生成的改动
3. 看一个 PR 有没有破坏基座

可直接复制：

```text
请对这次改动做代码审查，按“基座保护优先”的标准进行。

重点检查：
1. 是否破坏路由/菜单/权限/后端菜单树联动
2. 是否绕过脚手架和 registry 机制
3. 是否在主文件中堆入不必要的业务注册
4. meta.functionCode 与后端 permission 是否一致
5. 是否遗漏 baseline 验证或关键测试
6. 是否保留了脚手架占位字段、占位文案、占位 SQL

输出要求：
1. 先给 findings，按严重程度排序
2. 每条 finding 要带文件路径和原因
3. 再给开放问题或验证缺口
4. 最后才给简短总结
```

## 9. 回归验证模板

适用场景：

1. 功能改完了，想让 AI 统一做验收
2. 需要 AI 先跑本地验证，再总结结果

可直接复制：

```text
请对我刚完成的改动做本地回归验证，并汇报结果。

要求：
1. 根据改动范围判断需要运行哪些验证。
2. 如果涉及脚手架、router、menu、registry、backend main、shared request/auth 等共享基础设施，优先运行 bash scripts/verify_framework_baseline.sh。
3. 如果只是局部改动，也至少运行对应的类型检查、py_compile 或目标测试。
4. 汇报时请按下面格式输出：
   - 运行的命令
   - 每个命令的结果
   - 如果失败，失败原因是什么
   - 建议下一步怎么处理
```

## 10. 多 agent 并行模板

适用场景：

1. 任务较大
2. 想同时让多个 agent 分头推进

可直接复制：

```text
这次任务请按多 agent 并行方式执行，但要避免写域冲突。

请先拆分为以下几个子任务：
1. 一个 agent 负责梳理项目现状和联动点，不改代码。
2. 一个 agent 负责前端页面与前端 registry 修改。
3. 一个 agent 负责后端模块与后端 registry 修改。
4. 一个 agent 负责验证和 review。

要求：
1. 每个 agent 都要明确负责的文件范围。
2. 不要让多个 agent 同时改同一个主文件。
3. 主 agent 最后负责整合结果、跑验证并给出最终结论。
4. 结果要汇报：
   - 每个 agent 做了什么
   - 最终整合后的文件
   - 验证结果
```

## 11. 给 AI 的附加约束模板

如果你想让 AI 更贴近这个仓库的实际要求，可以在 prompt 末尾追加下面这段：

```text
仓库约束补充：
1. 中文回复。
2. 优先复用脚手架和 registry，不要无必要扩写主文件。
3. 所有 ID 字段保持 string 语义。
4. API 成功响应按 code = 0 或 200 处理。
5. 前端统一使用 @/ 路径别名。
6. 异步操作要保留完整错误处理。
7. 修改完成后必须说明验证情况。
```

## 12. 核心公式

> 好的 prompt 能把这个仓库的约束、接入点和验收方式一次说明白，让 AI 进入正确的工程上下文。
