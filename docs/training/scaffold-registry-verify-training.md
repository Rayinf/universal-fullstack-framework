# 脚手架、Registry 与验证闭环培训手册

本文专门讲“为什么这个仓库不建议手工堆模块”，以及三类脚手架、注册表机制、基座验收链路到底怎么配合。

## 1. 先讲结论：为什么这里不推荐手工复制页面

因为在这个仓库里，新增一个模块不只是“多一页”。

一个标准模块至少会牵涉：

1. 前端类型
2. 前端 API
3. 前端页面
4. 可选 Store
5. 前端路由
6. 前端菜单
7. 后端菜单注册
8. 后端 router 注册
9. 权限码一致性
10. 基座验证链路

如果继续手工复制老模块并到处改主文件，问题会很快出现：

1. 主文件越来越大
2. 并行开发冲突越来越多
3. 容易漏掉某个联动点
4. 很难自动化验证

所以这个仓库引入了三个关键机制：

1. 脚手架
2. registry
3. verify baseline

## 2. 三类脚手架分别干什么

### 2.1 后端脚手架

脚本：`backend/scripts/scaffold_backend_module.py`

适用场景：

1. 前端已经有页面，只缺后端接口
2. 要把旧的后端逻辑重构成统一模块结构
3. 本次变更只涉及后端，不涉及前端页面和菜单

默认生成内容：

1. `router.py`
2. `deps.py`
3. `helpers.py`
4. `serializers.py`
5. `routes/<module>_routes.py`
6. `services/errors.py`
7. `services/<module>_query_service.py`
8. `services/<module>_command_service.py`
9. `repositories/<module>_repo.py`

同时还会写入：

- `backend/app/bootstrap/scaffold_router_registry.py`

### 2.2 前端脚手架

脚本：`scripts/scaffold_frontend_module.py`

适用场景：

1. 后端接口已经存在
2. 要快速补一个标准 CRUD 页面
3. 需要同时补齐路由、菜单和权限接线

默认生成内容：

1. `src/types/<bucket>/<fileStem>.ts`
2. `src/api/<bucket>/<fileStem>.ts`
3. `src/views/<viewDir>/<ViewName>.vue`
4. `src/stores/<bucket>/<fileStem>.ts`，仅 `--with-store`

默认同时写入三处注册表：

1. `src/router/scaffoldedRoutes.ts`
2. `src/config/scaffoldMenuRegistry.ts`
3. `backend/app/modules/system_admin/scaffold_menu_registry.py`

### 2.3 全栈脚手架

脚本：`scripts/scaffold_fullstack_module.py`

适用场景：

1. 新增模块同时涉及前端和后端
2. 需要一次把页面、接口、菜单、路由、注册表接齐
3. 希望减少“只生成一半”的风险

它的特点不是另造一套模板，而是编排：

1. 后端脚手架
2. 前端脚手架
3. 注册表预检查
4. 失败回滚

对新人要强调一句话：

“只要任务是新增一个完整业务模块，默认优先考虑全栈脚手架。”

## 3. 典型命令应该怎么讲

培训时建议统一用 `quality_report` 做示例。

### 3.1 前端脚手架示例

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --menu-parent production \
  --route-path /production/quality-report \
  --route-name production-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

### 3.2 后端脚手架示例

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py quality_report \
  --tag "质检报告" \
  --resource-path /manage/api/qualityReport \
  --table-name quality_report_records
```

### 3.3 全栈脚手架示例

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --table-name quality_report_records \
  --menu-parent production \
  --route-path /production/quality-report \
  --route-name production-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

## 4. 新人必须理解的 registry 机制

### 4.1 什么是 registry

registry 可以理解为“稳定主文件旁边的追加入口”。

当前仓库里的关键注册表包括：

1. `src/router/scaffoldedRoutes.ts`
2. `src/config/scaffoldMenuRegistry.ts`
3. `backend/app/bootstrap/scaffold_router_registry.py`
4. `backend/app/modules/system_admin/scaffold_menu_registry.py`

### 4.2 为什么不用一直改主文件

因为以下文件都属于稳定聚合层：

1. `src/router/index.ts`
2. `src/config/menuConfig.ts`
3. `backend/app/bootstrap/router_registry.py`
4. `backend/app/modules/system_admin/menu.py`

如果每次新增模块都改这些主文件，会带来几个问题：

1. 合并冲突集中爆发
2. 结构越来越散
3. 脚手架难以稳定插入内容
4. 测试边界越来越模糊

### 4.3 registry 的设计好处

1. 主文件保持稳定
2. 新模块只做追加，不破坏聚合逻辑
3. 多人并行时冲突更小
4. 脚手架可以围绕固定 marker 精准写入
5. registry 本身可以单独测试

## 5. 生成完不等于完成

这是培训里最应该反复强调的一句话。

脚手架生成的是：

- 最小可运行骨架

不是：

- 真实业务模块最终形态

生成后必须马上替换的内容包括：

1. 默认字段 `name/code/status/remark`
2. 查询条件
3. 表格列定义
4. 表单字段
5. 校验规则
6. 错误提示文案
7. 后端真实 SQL 与字段映射

## 6. 新模块真正要同步检查的点

培训时建议把下面 7 点直接当成固定清单讲：

1. 前端路由是否写入 `scaffoldedRoutes.ts`
2. 前端菜单是否写入 `scaffoldMenuRegistry.ts`
3. 后端菜单是否写入 `scaffold_menu_registry.py`
4. 后端 router 是否写入 `scaffold_router_registry.py`
5. `meta.functionCode` 与后端 `permission` 是否完全一致
6. `menu_parent`、`route_path`、目录分桶是否一致
7. `frameworkConfig.ts` 是否允许该路由前缀

## 7. verify baseline 是什么

统一入口：

```bash
bash scripts/verify_framework_baseline.sh
```

它依次执行 5 步：

1. Python 编译检查
2. 后端基座回归
3. PostgreSQL HTTP smoke
4. 前端类型检查
5. 前端构建检查

成功时会输出：

```text
BASELINE_VERIFY_OK
```

## 8. 这 5 步分别在兜底什么风险

### 8.1 Python 编译检查

兜底：

1. 语法错误
2. import 错误
3. 脚手架或测试文件的基本可执行性

### 8.2 后端基座回归

兜底：

1. 脚手架生成逻辑是否仍正确
2. registry 合并逻辑是否仍正确
3. 模块路由注册是否仍正确

### 8.3 PostgreSQL HTTP smoke

兜底：

1. 应用是否真的能启动并对外提供关键接口
2. 登录、用户信息、菜单、刷新 token、本地 CRUD 是否真正打通

### 8.4 前端类型检查

兜底：

1. 生成文件或改动后的 TS 类型错误
2. Vue 组件与 Volar 类型问题

### 8.5 前端构建检查

兜底：

1. 真实生产构建是否通过
2. 动态导入、依赖、路径引用是否正确

## 9. 建议怎么做现场演示

### 9.1 第一段：先讲设计思想

别一上来跑命令。  
先让新人明白：

1. 主文件是稳定聚合层
2. registry 是追加入口
3. scaffold 是生成器
4. verify 是回归闸门

### 9.2 第二段：演示前端脚手架

演示重点：

1. 生成了哪些文件
2. 菜单和路由怎么自动接线
3. 为什么后端菜单注册也要一起写
4. 占位字段为什么必须马上替换

### 9.3 第三段：演示后端脚手架

演示重点：

1. 模块层结构
2. route、service、repo 分层职责
3. 为什么 router registry 是自动接入点

### 9.4 第四段：演示全栈脚手架

演示重点：

1. 一次命令生成前后端
2. 自动同步菜单、路由、权限码
3. 失败回滚意味着什么

### 9.5 第五段：演示统一验收

演示重点：

1. 生成完还必须过 baseline
2. 这不是形式主义，而是防止破坏基座

## 10. 新人最容易踩的坑

1. 把脚手架占位字段当成最终业务字段
2. 只生成页面，不检查权限码一致性
3. 跳过 registry，直接改主文件
4. 生成后不跑 verify baseline 就提交
5. `menu_parent`、`route_path`、目录分桶不一致
6. 误以为“页面能打开”就代表模块已经接完

## 11. 给受训同事的一句话总结

> 脚手架解决的是“如何标准化生成”，registry 解决的是“如何低冲突接线”，verify baseline 解决的是“如何证明没有把基座改坏”。
