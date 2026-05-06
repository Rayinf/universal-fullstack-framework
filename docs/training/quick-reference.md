# 新同事一页式速查表

## 1. 先记住项目定位

这个仓库是：

- 可扩展业务系统基座
- 包含前后端、权限菜单、脚手架、registry 和 baseline 验证的通用框架

## 2. 当前启用模块

截至 2026-03-16：

1. `system`
2. `sales`
3. `production`

未启用但保留规划：

1. `task`
2. `planning`
3. `process`
4. `quality`

## 3. 项目启动时先配置项目上下文

新项目启动时先完成项目配置，再新增业务模块。

输入模式：

1. 需规自动配置：从需求规格、产品 brief、会议纪要或用户故事中提取项目信息
2. 手动输入配置：由用户直接给出项目名称、slug、业务域、模块规划和默认路由

标准输出：

1. `project.manifest.yaml`
2. `docs/requirements.md`
3. `docs/agent-brief.md`
4. 项目名称、业务域、模块启用计划和 baseline 验证清单

关键原则：

先配置 `app_name`、`app_slug`、业务域和模块规划，再生成具体业务模块。

## 4. 新增模块时先判断用哪个脚手架

1. 只补后端：`backend/scripts/scaffold_backend_module.py`
2. 只补前端：`scripts/scaffold_frontend_module.py`
3. 前后端一起补：`scripts/scaffold_fullstack_module.py`

默认优先级：

完整新增模块时，优先用全栈脚手架。

## 5. 最重要的联动点

新增模块时至少检查这 7 项：

1. 前端路由
2. 前端菜单
3. 后端菜单注册
4. 后端 router 注册
5. 前端 `meta.functionCode`
6. 后端 `permission`
7. `frameworkConfig.ts` 是否允许该路由前缀

## 6. 四个关键 registry

1. `src/router/scaffoldedRoutes.ts`
2. `src/config/scaffoldMenuRegistry.ts`
3. `backend/app/bootstrap/scaffold_router_registry.py`
4. `backend/app/modules/system_admin/scaffold_menu_registry.py`

原则：

优先改 registry，尽量不把主文件重新改成大杂烩。

## 7. 权限问题先查哪里

出现“菜单不见了、页面进不去、被重定向”时，优先按下面顺序查：

1. `frameworkConfig.ts` 是否启用该前缀
2. 路由是否有正确的 `meta.functionCode`
3. 后端菜单树是否有对应 `permission`
4. 前后端权限码是否完全一致
5. 当前角色的 `allowedMenuIds` 是否包含对应菜单
6. 后端 `/admin/menu/tree` 与 `/admin/menu/tree/{roleId}` 返回是否正常

## 8. 默认验证命令

统一入口：

```bash
bash scripts/verify_framework_baseline.sh
```

它会做：

1. Python 编译检查
2. 后端基座回归
3. PostgreSQL HTTP smoke
4. 前端类型检查
5. 前端构建检查

成功标志：

```text
BASELINE_VERIFY_OK
```

## 9. 最容易踩的坑

1. 只改页面，不改联动链
2. `functionCode` 和 `permission` 不一致
3. 只配前端菜单，不配后端菜单树
4. 忘记 `frameworkConfig.ts`
5. 把脚手架占位字段当成真实业务字段
6. 生成完就提交，不跑 baseline
7. 把“菜单可见”误判为“权限正确”

## 10. 对 skill 的最短理解

skill 是：

- 可触发的标准工作流
- Agent 按框架约束工作的操作说明

## 11. 给 AI 的最小启动指令

如果你要让 AI 接手当前任务，至少先让它：

1. 读取 `AGENTS.md`
2. 读取 `CLAUDE.md`
3. 读取 `docs/training/ai-collaboration-guide.md`
4. 检查 `src/router/index.ts`、`src/config/frameworkConfig.ts`、`backend/app/modules/system_admin/menu.py`
5. 再开始具体任务

## 12. 先判断这件事属于哪一层

1. skill/仓库已明确规定
   让 AI 直接执行
2. 有方向但值不唯一
   让 AI 先提案，你确认
3. 会改变业务语义或基座边界
   你来拍板

## 13. 记忆公式

> 基座定结构，skill 定方法，脚手架做生成，registry 做接线，baseline 做兜底，AI 按这条链路工作。
