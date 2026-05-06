# 前端 CRUD 模块脚手架

当前仓库已提供标准前端 CRUD 模块脚手架，可直接生成 `types + api + view`，并按需接入 `Pinia store`。

如果当前任务是“新增一个完整业务模块”，同时还要补后端接口、后端 router、前后端菜单与注册表，优先使用 [`docs/fullstack-module-template.md`](fullstack-module-template.md) 对应的一键入口：

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py example_record \
  --tag "示例记录" \
  --api-base-path /manage/api/exampleRecord \
  --table-name example_records \
  --function-code APP-FUNC-EXAMPLE-RECORD \
  --with-store
```

当前文档对应的是“仅前端侧生成或补接前端模块”场景。

默认情况下，脚手架还会把新页面注册到：

- `src/router/scaffoldedRoutes.ts`
- `src/config/scaffoldMenuRegistry.ts`
- `backend/app/modules/system_admin/scaffold_menu_registry.py`

也就是说，生成后不需要再手工修改 `src/router/index.ts`、`src/config/menuConfig.ts` 和后端 `menu_tree()` 主体文件，只需要继续补真实业务字段与后端权限语义即可。

## 1. 生成命令

不带 Store：

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py example_record \
  --tag "示例记录" \
  --api-base-path /manage/api/exampleRecord
```

带 Store：

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py example_record \
  --tag "示例记录" \
  --api-base-path /manage/api/exampleRecord \
  --with-store
```

指定菜单分组并写入权限码：

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py example_record \
  --tag "示例记录" \
  --api-base-path /manage/api/exampleRecord \
  --menu-parent system \
  --route-path /system/example-record \
  --route-name system-example-record \
  --function-code APP-FUNC-EXAMPLE-RECORD
```

默认输出到：

```text
src/
├── api/system/exampleRecord.ts
├── types/system/exampleRecord.ts
├── views/system-admin/ExampleRecordManagement.vue
├── router/scaffoldedRoutes.ts        # 默认自动生成或追加
├── config/scaffoldMenuRegistry.ts    # 默认自动生成或追加
├── ../backend/app/modules/system_admin/scaffold_menu_registry.py
└── stores/system/qualityReport.ts    # 仅 --with-store 时生成
```

## 2. 默认参数

- `module_name`
  - 必填，使用 `snake_case`，例如 `quality_report`
- `--tag`
  - 页面与业务中文标签，例如 `质检报告`
- `--api-base-path`
  - 接口基础路径，例如 `/manage/api/qualityReport`
- `--api-dir`
  - `src/api/` 下子目录，默认 `system`
- `--type-dir`
  - `src/types/` 下子目录，默认 `system`
- `--view-dir`
  - `src/views/` 下子目录，默认 `system-admin`
- `--store-dir`
  - `src/stores/` 下子目录，默认 `system`
- `--file-stem`
  - 文件名 stem，默认把 `module_name` 转成 camelCase，例如 `qualityReport`
- `--entity-name`
  - 类型与函数名使用的 PascalCase 名称，例如 `QualityReport`
- `--view-name`
  - 页面文件名，默认 `<EntityName>Management`
- `--description`
  - 页面头部描述文案
- `--with-store`
  - 同时生成 Pinia Composition Store，并让页面接入 Store
- `--menu-parent`
  - 菜单挂载分组，支持 `root/system/sales/production`，默认 `system`；`sales`、`production` 是仓库内置示例业务桶，可按实际项目替换
- `--route-path`
  - 前端路由路径，默认根据 `menu-parent + module_name` 自动生成，例如 `/system/quality-report`
- `--route-name`
  - 前端路由名，默认自动生成，例如 `system-quality-report`
- `--function-code`
  - 路由与菜单权限码，留空则不写入 `functionCode`
- `--menu-id`
  - 前端菜单 ID，默认与 `route-name` 一致
- `--menu-title`
  - 前端菜单标题，默认使用 `<tag>管理`
- `--menu-icon`
  - 前端菜单图标，默认 `Document`
- `--skip-route-registration`
  - 只生成模块文件，不写入 `src/router/scaffoldedRoutes.ts`
- `--skip-menu-registration`
  - 只生成模块文件，不写入 `src/config/scaffoldMenuRegistry.ts`
- `--backend-menu-id`
  - 后端菜单 ID，默认与 `route-name` 一致
- `--skip-backend-menu-registration`
  - 只生成前端模块文件，不写入 `backend/app/modules/system_admin/scaffold_menu_registry.py`
- `--backend-root`
  - 后端根目录，默认 `./backend`

## 3. 生成出的默认内容

脚手架默认提供一套最小可运行 CRUD 样板，字段使用：

- `id`
- `name`
- `code`
- `status`
- `remark`

页面自带：

- 查询区
- 表格区
- 分页
- `usePageQuery` 查询/分页动作封装
- 新增/编辑弹窗
- 详情弹窗
- 删除确认
- `@import '@/styles/common.css'`
- `FormDialog` / `BaseDialog` 复用

路由 / 菜单默认接入方式：

- `src/router/index.ts` 统一 `import { scaffoldedRoutes } from '@/router/scaffoldedRoutes'`
- `src/config/menuConfig.ts` 统一 `import { scaffoldedMenuRegistry } from '@/config/scaffoldMenuRegistry'`
- `backend/app/modules/system_admin/menu.py` 统一聚合 `scaffold_menu_registry.py`
- 新脚手架模块只向注册表追加，不直接改主配置大文件

## 4. 生成后必须立即替换的部分

不要把默认样板直接作为最终业务代码保留，至少要替换：

- 页面标题与描述
- 查询字段
- 列表列定义
- 表单字段与校验规则
- 接口路径和错误文案

## 5. 联动检查清单

新增页面后，必须同步检查：

1. 前端注册表：`src/router/scaffoldedRoutes.ts`
2. 前端注册表：`src/config/scaffoldMenuRegistry.ts`
3. 后端菜单注册表 / 权限码：`backend/app/modules/system_admin/scaffold_menu_registry.py`
4. 布局过滤与守卫：`src/layouts/MainLayout.vue`、`src/config/frameworkConfig.ts`

否则常见症状会是：

- 页面文件已生成，但菜单不可见
- 菜单可见，但点击后被守卫重定向
- 路由可达，但按钮权限不生效

## 6. 推荐生成流程

推荐固定按下面顺序走，避免只生成页面不接线：

1. 先确定后端接口路径、权限码、菜单分组。
2. 运行 `scaffold_frontend_module.py`，默认让它自动写入路由 / 菜单注册表。
3. 替换模板中的字段、列、表单与错误文案。
4. 同步确认后端菜单注册和 `meta.functionCode` / `permission` 一致。
5. 跑类型检查并手工点开页面验收。

## 7. 建议提交流程

```bash
./backend/.venv/bin/python -m py_compile scripts/scaffold_frontend_module.py backend/tests/test_frontend_scaffold.py
./backend/.venv/bin/python -m unittest backend.tests.test_frontend_scaffold -v
npm run type-check
```
