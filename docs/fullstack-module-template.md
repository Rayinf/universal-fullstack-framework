# 一键全栈模块脚手架

当前仓库已提供一键全栈模块脚手架：

- 脚本：`scripts/scaffold_fullstack_module.py`
- 目标：一次命令同时生成后端模块骨架、前端 CRUD 骨架，并完成前后端注册表接线

如果新增模块同时涉及前端页面、后端接口、路由、菜单、权限接线，优先使用这个入口。  
只有在“仅补前端页面”或“仅补后端模块”时，再分别使用单边脚手架。

## 1. 推荐命令

系统管理模块：

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --table-name quality_report_records \
  --menu-parent system \
  --route-path /system/quality-report \
  --route-name system-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

生产模块：

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --table-name quality_report_records \
  --menu-parent production \
  --route-path /production/quality-report \
  --route-name production-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --menu-icon DataAnalysis \
  --with-store
```

## 2. 默认会生成什么

后端：

- `backend/app/modules/<module_name>/router.py`
- `backend/app/modules/<module_name>/deps.py`
- `backend/app/modules/<module_name>/helpers.py`
- `backend/app/modules/<module_name>/serializers.py`
- `backend/app/modules/<module_name>/routes/<module_name>_routes.py`
- `backend/app/modules/<module_name>/services/*`
- `backend/app/modules/<module_name>/repositories/<module_name>_repo.py`
- `backend/app/bootstrap/scaffold_router_registry.py`

前端：

- `src/types/<bucket>/<fileStem>.ts`
- `src/api/<bucket>/<fileStem>.ts`
- `src/views/<viewDir>/<ViewName>.vue`
- `src/stores/<bucket>/<fileStem>.ts`（仅 `--with-store`）
- `src/router/scaffoldedRoutes.ts`
- `src/config/scaffoldMenuRegistry.ts`
- `backend/app/modules/system_admin/scaffold_menu_registry.py`

## 3. 默认目录映射

脚手架会根据 `--menu-parent` 自动给前端目录分桶，必要时可再手工覆盖：

- `root`
  - `api/type/store`: `system`
  - `view`: `system`
- `system`
  - `api/type/store`: `system`
  - `view`: `system-admin`
- `sales`
  - `api/type/store`: `sales`
  - `view`: `sales`
- `production`
  - `api/type/store`: `production`
  - `view`: `production`

## 4. 常用参数

- `module_name`
  - 必填，`snake_case`
- `--tag`
  - 前后端共用业务标签
- `--api-base-path` / `--resource-path`
  - 前后端共用接口前缀
- `--table-name`
  - 后端默认表名
- `--menu-parent`
  - 菜单分组：`root/system/sales/production`
- `--route-path`
  - 前端路由路径
- `--route-name`
  - 前端路由名，同时默认作为前后端菜单 ID
- `--function-code`
  - 前端 `meta.functionCode` 与后端 `permission` 共用权限码
- `--menu-title`
  - 前后端菜单标题
- `--menu-icon`
  - 前端菜单图标
- `--with-store`
  - 同时生成 Pinia Store

## 5. 生成后必须马上做的事

- 替换默认字段：`name/code/status/remark`
- 替换默认表单、表格、查询项与错误文案
- 确认后端真实表结构、SQL 字段和接口参数
- 确认 `meta.functionCode` 与后端 `permission` 完全一致
- 确认菜单挂载分组与页面目录符合业务域

## 6. 推荐流程

1. 先确定接口前缀、菜单分组、权限码、表名。
2. 优先运行 `scaffold_fullstack_module.py`。
3. 补真实业务字段与 SQL。
4. 跑脚手架测试与目标模块回归。
5. 手工打开菜单、页面、接口链路做 smoke。

## 7. 验证命令

```bash
./backend/.venv/bin/python -m py_compile \
  scripts/scaffold_fullstack_module.py \
  backend/tests/test_fullstack_scaffold.py

./backend/.venv/bin/python -m unittest backend.tests.test_fullstack_scaffold -v

npm run type-check
```

如果只改了脚手架本身而未生成真实页面到当前仓库，可先只跑前两条。
