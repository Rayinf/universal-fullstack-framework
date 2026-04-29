# 通用前后端开发基座评估与改进路线（Vue 3 + FastAPI）

更新时间：2026-03-11

## 1. 文档目的

本文件用于持续评估当前仓库是否已经具备“可复用业务系统基座”的条件，并明确：

- 当前已经稳定落地的能力
- 仍然存在的结构性短板
- 下一阶段最值得继续投入的改造方向

目标不是写一份静态总结，而是为后续多轮重构提供统一判断基线。

## 2. 当前结论（先看这个）

### 2.1 是否已经适合作为通用基座继续演进

结论：**可以继续作为通用基座推进，不需要推倒重来。**

当前已经具备：

- 前后端统一技术栈
- 后端模块化路由骨架
- 前后端/全栈脚手架
- PostgreSQL-only 运行链路
- 最小 CI 与本地基线验收链路

但距离“完整的平台化基座”还有差距，主要缺口集中在：

- 初始化链路总量仍然偏大
- 数据访问层尚未完全标准化
- 发布/回滚/灰度策略未形成
- 结构化日志、指标、告警未形成闭环
- 多租户/多组织隔离尚未开始

### 2.2 `main.py` 拆分是否完成

结论：**已完成“入口文件拆分”这一目标，但未完成“整个后端深度治理”的全部工作。**

当前证据：

- `backend/main.py` 当前约 **210 行**
- 路由挂载已统一下沉到 `backend/app/bootstrap/router_registry.py`
- 业务路由已拆分到 `backend/app/modules/*`
- `main.py` 当前主要职责只剩：
  - 环境变量加载
  - 安全与中间件初始化
  - 数据库运行时装配
  - 路由统一注册
  - 启动时 `init_db()` 调用

所以，如果问题是“`main.py` 还是不是那个 1w+ 行巨石文件”，答案是否定的；这部分拆分已经完成。

但如果问题是“后端是不是已经彻底拆干净”，答案是否定的。尚未完成的深层工作主要还有：

- `backend/app/bootstrap/init_db.py` 已收敛到约 **37 行**
- `backend/app/bootstrap/init_db_schema.py` 已收敛到约 **15 行** 的 schema 编排入口
- `backend/app/bootstrap/init_db_seed.py` 已收敛到约 **31 行** 的编排入口
- 初始化 schema 已按域拆分为：
  - `backend/app/bootstrap/init_db_schema_system.py`
  - `backend/app/bootstrap/init_db_schema_demo_common.py`
  - `backend/app/bootstrap/init_db_schema_sales.py`
  - `backend/app/bootstrap/init_db_schema_production.py`
- 初始化 seed 已按域拆分为：
  - `backend/app/bootstrap/init_db_seed_system.py`
  - `backend/app/bootstrap/init_db_seed_demo_common.py`
  - `backend/app/bootstrap/init_db_seed_sales.py`
  - `backend/app/bootstrap/init_db_seed_production.py`
- 部分历史 SQL 仍依赖 `backend/app/infra/db.py` 中的 legacy SQL 兼容转换
- 模块级 repository/service 的边界虽已建立，但还没有做到完全统一规范

## 3. 当前基座能力（已落地）

### 3.1 技术栈统一

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus
- 后端：Python + FastAPI
- 数据库：**PostgreSQL-only**

SQLite 已不再作为运行选项保留。

### 3.2 后端分层骨架已形成

当前后端目录已经形成明确结构：

- `backend/app/core`：认证、响应、异常、中间件、安全/OpenAPI 等核心能力
- `backend/app/infra`：数据库运行时、兼容层、数据库异常统一封装
- `backend/app/bootstrap`：数据库初始化、路由注册、启动装配
- `backend/app/modules/<domain>`：按业务域拆分 router/service/repository

当前已存在的业务模块 router 已超过 20 个，包含：

- 系统与认证
- 系统管理（用户/角色/菜单/部门）
- 客户、工位、设备、基础资料、工艺库、扫码绑定、编码规则
- 项目、采购、库存、产品目录、报价、合同、佣金、回款
- 工单、报工、入库、通知、附件
- 备份、日志、审批流

### 3.3 PostgreSQL-only 已收口

本轮之前残留的 SQLite 运行路径已经清理完成，当前状态为：

- `backend/main.py` 固定走 PostgreSQL
- `backend/app/infra/db.py` 固定走 PostgreSQL
- `package.json` 仅保留 PostgreSQL 后端启动命令
- SQLite 启动入口、迁移脚本、本地回退库文件已删除

为了降低一次性改写全部 SQL 的风险，当前仍保留一层最小兼容转换，集中在 `backend/app/infra/db.py`：

- `?` 占位符转换为 PostgreSQL 参数形式
- `INSERT OR IGNORE` 转换为 `ON CONFLICT DO NOTHING`
- `PRAGMA table_info(...)` 转换为 PostgreSQL 元数据查询

这使得系统已经是 PostgreSQL-only，但仍处于“历史 SQL 平滑过渡期”。

### 3.4 脚手架与注册表机制已落地

当前已经具备三类生成能力：

- 后端脚手架：`backend/scripts/scaffold_backend_module.py`
- 前端脚手架：`scripts/scaffold_frontend_module.py`
- 全栈脚手架：`scripts/scaffold_fullstack_module.py`

并且脚手架不是简单复制模板，而是已经打通注册链路：

- 前端路由注册：`src/router/scaffoldedRoutes.ts`
- 前端菜单注册：`src/config/scaffoldMenuRegistry.ts`
- 后端菜单注册：`backend/app/modules/system_admin/scaffold_menu_registry.py`
- 后端路由注册：`backend/app/bootstrap/scaffold_router_registry.py`

也就是说，新增模块已经从“手工复制粘贴”进入“带注册表的半自动生成”阶段。

### 3.5 最小工程化验收链路已落地

当前已经具备一条可以直接执行的基线验收链路：

- 本地统一脚本：`scripts/verify_framework_baseline.sh`
- CI 工作流：`.github/workflows/ci.yml`
- 说明文档：`docs/ci-baseline.md`

当前基线会覆盖：

1. Python 编译检查
2. 后端模块化回归
3. PostgreSQL 真实 HTTP smoke
4. 前端类型检查
5. 前端生产构建检查

其中 `backend/tests/test_http_smoke.py` 已覆盖真实 `uvicorn + PostgreSQL` 启动后的核心链路：

- `/health`
- `/auth/oauth2/token`
- `/admin/user/info`
- `/admin/menu/tree`
- `/auth/oauth2/refresh`
- `/local/crud/page`
- `/local/crud`

2026-03-11 本地已再次验证：

- 后端组合回归 `60/60` 通过
- PostgreSQL HTTP smoke `1/1` 通过
- `bash scripts/verify_framework_baseline.sh` 输出 `BASELINE_VERIFY_OK`

### 3.6 认证链路基础稳定性增强

本轮还修复了一个真实问题：

- 同一秒刷新 access token 时，旧实现可能生成完全相同的 JWT
- 现已在 `backend/app/core/auth.py` 中加入随机 `jti`
- 已补充单测，确保 refresh 后的新 token 唯一，单点登录互踢逻辑有效

## 4. 当前仍需关注的问题与风险

### P0：仍会影响长期复用效率的问题

#### 4.1 初始化逻辑仍然偏重

- `backend/app/bootstrap/init_db.py` 已收敛成编排入口
- `backend/app/bootstrap/init_db_schema.py` 与 `backend/app/bootstrap/init_db_seed.py` 也都已经收敛成编排入口
- schema 与 seed 都已拆成 system/demo_common/sales/production 四个域模块
- 但初始化相关总量仍然偏大，下一步更适合继续把各域 schema/seed 向更细业务子域或表组拆分，而不是再回头动 `main.py`

#### 4.2 数据访问层尚未完全标准化

- 许多模块已经具备 repository/service 分层
- 但 SQL 风格尚未完全统一
- 当前仍依赖 `backend/app/infra/db.py` 的 legacy SQL 兼容层兜底

这说明“架构方向”已经对了，但“数据访问治理”还没彻底收尾。

#### 4.3 接口契约尚未完全一致

当前大多数接口已统一为：

```json
{ "code": 0, "msg": "success", "data": ... }
```

但认证接口仍存在特例，例如：

- `/auth/oauth2/token` 返回的是 OAuth 风格 token dict
- `/auth/oauth2/refresh` 返回结构与普通 CRUD 包装并不完全一致

这意味着“统一响应协议”已经大体形成，但还不是 100% 严格一致。

### P1：决定团队协作效率的问题

#### 4.4 页面模板体系还不够厚

虽然前后端/全栈脚手架已经落地，但当前更偏“生成基础 CRUD 骨架”，还没有完全形成下面这些高复用模板：

- 列表 + 明细抽屉
- 列表 + 表单弹窗 + 附件面板
- 审批流页面模板
- 仪表盘/统计页模板

#### 4.5 发布/回滚/灰度还没有真正落地

当前已经有：

- 本地验收脚本
- GitHub Actions CI
- PostgreSQL HTTP smoke

但还没有：

- 数据库迁移工具链（如 Alembic）
- 标准化发布脚本
- 回滚脚本
- 灰度/分环境部署策略

#### 4.6 可观测性仍然不足

虽然已经有 `sys_log` 等模块，但距离“生产问题可快速定位”还有明显差距：

- 缺少结构化应用日志
- 缺少指标采集
- 缺少统一告警规则
- 缺少 trace/request id 贯通

### P2：平台化能力缺口

#### 4.7 多租户/多组织隔离尚未开始

当前系统仍然主要按单租户/单业务实例思路组织，没有形成：

- 租户隔离模型
- 组织级隔离策略
- 按租户的菜单/数据/配置装配机制

#### 4.8 插件化还处于“注册表驱动”而非“真正插件化”

当前脚手架 + 注册表已经很好用，但仍属于“代码级注册”：

- 需要写入前后端注册表
- 还不是安装模块即自动发现/自动装配

所以它已经迈出了平台化第一步，但还没到“插件平台”的程度。

## 5. 分阶段实施进度（持续更新）

最后更新：2026-03-11

### 阶段 A：稳住基座

- [x] A1 后端分层骨架初始化
- [x] A2 统一响应与异常处理入口
- [x] A3 首个系统路由拆分落地
- [x] A4 核心业务路由模块化迁移
- [x] A5 后端最小自动化测试补齐
- [x] A6 环境变量模板与启动说明固化
- [x] A7 PostgreSQL-only 收口
- [x] A8 `init_db.py` 首轮拆分（seed 外移到独立模块）
- [x] A9 `init_db_seed.py` 二轮拆分（按系统/通用/销售/生产分域）
- [x] A10 `init_db_schema.py` 三轮拆分（按系统/通用/销售/生产分域）

阶段 A 结论：

- `main.py` 巨石问题已解除
- 模块化路由结构已成型
- 后端已不再依赖 SQLite 运行路径

### 阶段 B：提升复用效率

- [x] B1 前后端/全栈脚手架落地
- [ ] B2 通用业务页面模板继续提炼
- [ ] B3 统一业务组件与设计规范继续沉淀

阶段 B 当前结论：

- “新模块从零搭骨架”这件事已经有脚手架支持
- 但“生成后即可进入统一高质量业务开发”的模板厚度还不够

### 阶段 C：平台化与生产增强

- [ ] C1 结构化日志、指标、告警体系
- [x] C2a 最小本地基线验收脚本
- [x] C2b GitHub Actions CI 与 PostgreSQL HTTP smoke
- [ ] C2c 发布回滚与灰度策略
- [ ] C3 多租户/多组织隔离

阶段 C 当前结论：

- 工程化入口已经有了
- 但还没有形成完整的发布平台能力

## 6. 下一阶段最值得继续做的事

按性价比排序，建议优先做下面 5 件事：

1. 继续细化各域 `init_db_schema_*` / `init_db_seed_*`，把 DDL/补列与 seed 继续向更小业务子域或表组下沉
2. 逐模块清理 legacy SQL，减少对 `backend/app/infra/db.py` 兼容层的依赖
3. 统一认证相关接口契约，减少响应结构特例
4. 补齐结构化日志/审计日志/关键指标埋点
5. 引入数据库迁移工具，补发布与回滚流程

如果只能选一个继续推进，优先级建议是：

**先继续细化初始化链路（优先各域 `init_db_schema_*`/`init_db_seed_*` 的进一步收敛），然后逐步消化 legacy SQL。**

原因很简单：

- `main.py` 已经瘦身成功，不再是当前最大的结构风险
- 当前最大的后端大文件风险仍在初始化链路，但已经从“单个超大文件”转为“多域 schema + 多域 seed 的总复杂度”
- PostgreSQL-only 已收口，接下来最该做的是把过渡层慢慢吃掉

## 7. 当前验收门槛（建议）

任何较大改动至少应通过以下检查：

- `python3 -m py_compile backend/main.py`
- `backend/.venv/bin/python -m unittest ...`
- `backend/.venv/bin/python -m unittest backend.tests.test_http_smoke -v`
- `npm run type-check`
- `npm run build-only`
- `bash scripts/verify_framework_baseline.sh`

其中最后一条可以作为日常统一入口。

## 8. 评估依据（关键文件）

- 后端入口：`backend/main.py`
- 路由注册中心：`backend/app/bootstrap/router_registry.py`
- 数据库运行时：`backend/app/infra/db.py`
- 数据库异常统一层：`backend/app/infra/db_errors.py`
- 数据初始化入口：`backend/app/bootstrap/init_db.py`
- 初始化 schema 编排入口：`backend/app/bootstrap/init_db_schema.py`
- schema 公共辅助：`backend/app/bootstrap/init_db_schema_shared.py`
- 系统 schema：`backend/app/bootstrap/init_db_schema_system.py`
- 通用 schema：`backend/app/bootstrap/init_db_schema_demo_common.py`
- 销售 schema：`backend/app/bootstrap/init_db_schema_sales.py`
- 生产 schema：`backend/app/bootstrap/init_db_schema_production.py`
- 初始化 seed 编排入口：`backend/app/bootstrap/init_db_seed.py`
- 系统 seed：`backend/app/bootstrap/init_db_seed_system.py`
- 通用 seed：`backend/app/bootstrap/init_db_seed_demo_common.py`
- 销售 seed：`backend/app/bootstrap/init_db_seed_sales.py`
- 生产 seed：`backend/app/bootstrap/init_db_seed_production.py`
- 后端脚手架：`backend/scripts/scaffold_backend_module.py`
- 前端脚手架：`scripts/scaffold_frontend_module.py`
- 全栈脚手架：`scripts/scaffold_fullstack_module.py`
- 基线验收脚本：`scripts/verify_framework_baseline.sh`
- CI：`.github/workflows/ci.yml`
- 验收说明：`docs/ci-baseline.md`
- 模块化回归：`backend/tests/test_modular_routes.py`
- 真实 HTTP smoke：`backend/tests/test_http_smoke.py`

## 9. 最终判断

当前仓库已经从“业务项目”进入“可复用基座”的阶段，且关键转折点已经完成：

- `main.py` 不再是巨石文件
- 路由模块化已成型
- PostgreSQL-only 已收口
- 脚手架与注册表机制已落地
- 本地基线 + CI + HTTP smoke 已落地

接下来不应再回到“大而全混改”的方式，而应进入“按风险最高的剩余点逐个清理”的阶段。

当前最核心的后续任务不是再拆 `main.py`，而是：

- 继续细化初始化链路（优先各域 `init_db_schema_*` / `init_db_seed_*`）
- 吃掉 legacy SQL 兼容层
- 补生产工程化能力
