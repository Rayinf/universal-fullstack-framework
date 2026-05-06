# Universal Fullstack Framework

Universal Fullstack Framework 是一套面向企业管理系统的可复用全栈基座和 Agent Skill。它把存量 Vue 3 / TypeScript 管理系统收敛为稳定核心，再用脚手架和验证链路支持后续业务模块增量扩展。

这个仓库包含两部分：

- `framework base`：Vue 3 + TypeScript + Element Plus + Pinia 前端，FastAPI + PostgreSQL 后端，核心系统管理、示例业务域和本地 CRUD 演示。
- `agent skill`：`skills/universal-fullstack-framework/SKILL.md`，用于指导 Agent 完成代码库扫描、前后端契约对齐、模块脚手架生成、权限/菜单/路由接线、验证闭环。

仓库中保留的 `sales`、`production` 等分组是示例业务桶，用于展示模块分桶、菜单挂载、路由前缀和权限码如何协同工作。实际项目可按自己的业务域命名和裁剪。

## Core Value

企业后台项目常见问题包括接口漂移、路由与菜单配置分散、权限码错配、Mock 与真实后端割裂、CRUD 模块重复开发、上线前验收链路薄弱。这个框架把这些工程动作固化为可执行流程：

1. 冻结核心系统管理能力。
2. 盘点前端 API、路由、菜单、权限与后端 router/service/repository。
3. 建立前后端接口契约。
4. 用脚手架生成后端模块、前端 types/api/view/store、路由注册、菜单注册和权限码。
5. 通过 Python 编译、后端单测、HTTP smoke、Vue 类型检查和构建检查做闭环验证。

## Repository Layout

```text
.
├── backend/                         # FastAPI backend
│   ├── app/modules/                 # Modular backend domains
│   ├── docs/backend-module-template.md
│   ├── scripts/scaffold_backend_module.py
│   └── tests/
├── src/                             # Vue 3 frontend
│   ├── api/
│   ├── config/
│   ├── router/
│   ├── stores/
│   ├── types/
│   └── views/
├── scripts/
│   ├── scaffold_frontend_module.py
│   ├── scaffold_fullstack_module.py
│   └── verify_framework_baseline.sh
├── scaffolds/frontend_module/        # Frontend scaffold templates
├── skills/universal-fullstack-framework/SKILL.md
├── docs/fullstack-module-template.md
├── docs/frontend-module-template.md
├── docs/skill-usage.md
├── docs/ci-baseline.md
├── docs/github-actions-ci.yml
└── FRAMEWORK_GUIDE.md
```

## Quick Start

```bash
npm install

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..

cp .env.example .env
npm run backend:dev
npm run dev
```

Default local endpoints:

- Frontend: `http://127.0.0.1:5174`
- Backend API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

Default demo account:

- Username: `admin`
- Password: `admin123`

## Scaffold A Fullstack Module

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

The command generates:

- backend router/deps/helpers/serializers/routes/services/repository
- frontend types/api/view/store
- frontend route registry
- frontend menu registry
- backend menu registry
- aligned permission code

Then replace placeholder fields (`name/code/status/remark`) with real business fields and run validation.

## Validation

```bash
bash scripts/verify_framework_baseline.sh
```

The baseline gate runs:

1. Python compile checks.
2. Backend scaffold and modular route tests.
3. PostgreSQL HTTP smoke tests.
4. `npm run type-check`.
5. `npm run build-only`.

Successful output ends with:

```text
BASELINE_VERIFY_OK
```

## Agent Skill

The packaged skill is available at:

```text
skills/universal-fullstack-framework/SKILL.md
```

Use it when an Agent needs to start a concrete project from requirements or manual configuration, refactor a business system into a stable fullstack framework, add a new CRUD-style module, repair route/menu/API integration faults, or harden auth/JWT/CORS before deployment.

For prompt templates and recommended workflows, read [Skill Usage](docs/skill-usage.md).

## More Docs

- [Framework Guide](FRAMEWORK_GUIDE.md)
- [Fullstack Module Template](docs/fullstack-module-template.md)
- [Frontend Module Template](docs/frontend-module-template.md)
- [Skill Usage](docs/skill-usage.md)
- [Backend Module Template](backend/docs/backend-module-template.md)
- [CI Baseline](docs/ci-baseline.md)
- [GitHub Actions CI Example](docs/github-actions-ci.yml)
- [Project Start Playbook](skills/universal-fullstack-framework/references/project-start-playbook.md)
- [Original Base Project README](docs/base-project-readme.md)
