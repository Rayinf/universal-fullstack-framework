# 后端模块化模板

本模板用于在当前仓库内快速新增或重构一个标准后端模块，目标结构统一为：

```text
backend/app/modules/<domain>/
├── router.py
├── deps.py
├── helpers.py
├── serializers.py
├── routes/
│   └── <domain>_routes.py
├── services/
│   ├── errors.py
│   ├── <domain>_query_service.py
│   └── <domain>_command_service.py
└── repositories/
    └── <domain>_repo.py
```

如果当前任务还包括前端 CRUD 页面、前端路由菜单、后端菜单注册，优先使用根目录的一键全栈脚手架：

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --table-name quality_report_records \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

当前文档对应的是“仅后端侧生成或重构模块”场景。完整流程见 [`docs/fullstack-module-template.md`](../../docs/fullstack-module-template.md)。

## 1. 各层职责

- `router.py`
  - 只负责 `APIRouter` 创建、依赖装配、调用 `register_*_routes(...)`
  - 对外暴露 `create_*_router(...)`，尽量保持原函数签名不变
- `deps.py`
  - 用 `dataclass` 收口路由依赖
  - 所有 `ok_func/fail_func/get_conn_func/now_str_func/...` 都在这里定义
- `helpers.py`
  - 放纯函数型解析逻辑，如分页参数标准化、payload 解析、字段映射
  - 不直接做 SQL
- `serializers.py`
  - 负责数据库行到接口返回结构的映射
  - 负责分页返回结构构造
- `routes/*.py`
  - 只做 HTTP 入参读取、调用 service、`ok/fail` 包装
  - 不直接写 SQL
- `services/*_query_service.py`
  - 负责查询型业务编排
  - 严格控制多条 SQL 的调用顺序，避免破坏现有测试
- `services/*_command_service.py`
  - 负责写入型业务、校验、事务提交、异常转译
- `services/errors.py`
  - 定义模块级业务异常，例如 `<Domain>ServiceError(message, code)`
- `repositories/*_repo.py`
  - 只收口 SQL，不做业务判断

## 2. 标准创建顺序

1. 先保留原 `create_*_router(...)` 的对外签名。
2. 提取 `deps.py`，让顶层 router 变成薄装配。
3. 把原路由函数迁到 `routes/*_routes.py`。
4. 把纯解析逻辑迁到 `helpers.py`。
5. 把响应组装迁到 `serializers.py`。
6. 把查询逻辑迁到 `*_query_service.py`。
7. 把写逻辑、校验、事务迁到 `*_command_service.py`。
8. 把 SQL 全部收口到 `repositories/*_repo.py`。
9. 补定向单测，再跑全量回归。

## 2.1 脚手架命令

当前仓库已提供可执行脚手架：

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py quality_report \
  --tag "质检报告" \
  --resource-path /manage/api/qualityReport \
  --table-name quality_report_records
```

常用参数：

- `module_name`
  - 目标模块名，必须是 `snake_case`
- `--tag`
  - 生成到 `APIRouter(tags=[...])` 的标签名
- `--resource-path`
  - 生成默认接口路径，例如 `/manage/api/qualityReport`
- `--table-name`
  - 生成仓储层默认 SQL 表名
- `--output-root`
  - 可选，默认输出到 `backend/app/modules/`

脚手架会自动生成：

- `router.py`
- `deps.py`
- `helpers.py`
- `serializers.py`
- `routes/<module_name>_routes.py`
- `services/errors.py`
- `services/<module_name>_query_service.py`
- `services/<module_name>_command_service.py`
- `repositories/<module_name>_repo.py`

生成模块后，如该模块需要出现在导航菜单中，还应同步：

- 在 `backend/app/bootstrap/scaffold_router_registry.py` 注册新 router
- 在 `backend/app/modules/system_admin/scaffold_menu_registry.py` 注册后端菜单项
- 与前端 `meta.functionCode` 使用同一套 `permission` 编码

## 3. 最小骨架示例

```python
# router.py
from fastapi import APIRouter

from app.modules.example.deps import ExampleRouterDeps
from app.modules.example.routes.example_routes import register_example_routes


def create_example_router(ok_func, fail_func, get_conn_func):
  router = APIRouter(tags=['示例模块'])
  deps = ExampleRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
  )
  register_example_routes(router, deps)
  return router
```

```python
# routes/example_routes.py
from fastapi import APIRouter, Request

from app.modules.example.services.example_query_service import query_example_page
from app.modules.example.services.errors import ExampleServiceError


def register_example_routes(router: APIRouter, deps) -> None:
  @router.get('/example/page')
  def page(current: int = 1, size: int = 10):
    try:
      return deps.ok_func(query_example_page(deps, current=current, size=size), 'success')
    except ExampleServiceError as error:
      return deps.fail_func(error.message, error.code)
```

## 4. 兼容性红线

- 不改接口路径。
- 不改成功/失败返回结构。
- 不改关键错误文案。
- 不改测试依赖的 SQL 调用顺序。
- 不改外部 import 入口和 `create_*_router(...)` 名称。

## 5. 推荐参考模块

- `system`：认证 + 配置 + 健康检查的薄装配样板
- `system_admin`：菜单/部门/角色/用户的多路由拆分样板
- `process`：纯查询模块的最轻量样板
- `quotation`、`contracts`、`work_order`：复杂业务模块样板

## 6. 提交前检查

```bash
./backend/.venv/bin/python -m py_compile $(rg --files backend/app/modules/<domain> | sort)
./backend/.venv/bin/python -m unittest backend.tests.test_modular_routes.ModularRoutesTestCase.<target_test> -v
./backend/.venv/bin/python -m unittest discover -s backend/tests -p 'test_*.py' -v
```
