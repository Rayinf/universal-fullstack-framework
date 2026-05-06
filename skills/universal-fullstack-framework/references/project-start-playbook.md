# Project Start Playbook

Use this playbook when starting a concrete business system from Universal Fullstack Framework.

The goal is to turn requirements or manual project configuration into a stable project manifest, initial framework configuration, Agent brief, and validation plan.

## 1. Input Modes

### 1.1 Requirements-driven mode

Use when the user provides a requirements document, product brief, meeting notes, screenshots, user stories, or a rough written idea.

Extract these fields:

- `project.app_name`
- `project.app_slug`
- `project.company_name`
- `project.description`
- `project.default_route`
- `requirements.audience`
- `requirements.pain_points`
- `requirements.core_modules`
- `requirements.acceptance`

For each module, extract:

- `id`
- `title`
- `route_prefix`
- `enabled`
- `description`
- `primary_entities`
- `minimum_workflows`
- `permission_prefix`
- `api_base_path`

Ask the user only for fields that block file generation:

- missing `app_name`
- missing or invalid `app_slug`
- no clear first enabled module beyond `system`
- ambiguous default route

Use conservative defaults for other values.

### 1.2 Manual configuration mode

Use when the user provides explicit configuration values.

Accept fields such as:

- `app_name`
- `app_slug`
- `company_name`
- `description`
- `default_route`
- `enabled_modules`
- `planned_modules`
- module route prefixes
- module function code prefix
- initial CRUD entity fields

If values are incomplete, normalize what is present and generate a clear `open_questions` section in the manifest.

## 2. Manifest Schema

Recommended file:

```text
project.manifest.yaml
```

Recommended schema:

```yaml
project:
  app_name: "服务管理系统"
  app_slug: "service_ops"
  company_name: "示例企业"
  description: "面向服务团队的客户、服务请求、知识库和回访管理系统"
  default_route: "/system/basic-crud"
  language: "zh-CN"

requirements:
  source:
    type: "manual" # manual | requirements_doc | meeting_notes | user_stories
    path: ""
  audience:
    - "服务专员"
    - "客服"
    - "管理层"
  pain_points:
    - "客户资料分散"
    - "服务处理进度不可见"
  core_modules:
    - id: "system"
      title: "系统管理"
      route_prefix: "/system"
      enabled: true
      description: "用户、角色、菜单、权限和系统配置"
      primary_entities:
        - "用户"
        - "角色"
      minimum_workflows:
        - "管理员维护用户和角色"
      permission_prefix: "APP-FUNC-SYSTEM"
      api_base_path: "/manage/api/system"
    - id: "customer"
      title: "客户管理"
      route_prefix: "/customer"
      enabled: true
      description: "客户档案、联系人和跟进记录"
      primary_entities:
        - "客户"
        - "联系人"
      minimum_workflows:
        - "客户新增、编辑、查询、删除"
      permission_prefix: "APP-FUNC-CUSTOMER"
      api_base_path: "/manage/api/customer"
  acceptance:
    - "管理员可配置用户和角色"
    - "客户列表支持新增、编辑、查询、删除"
  open_questions: []
```

## 3. Generated Files

Expected project-start outputs:

```text
project.manifest.yaml
docs/requirements.md
docs/agent-brief.md
```

`docs/requirements.md` should include:

- project overview
- target users
- pain points
- module plan
- first enabled modules
- acceptance criteria
- open questions

`docs/agent-brief.md` should include:

- project name and slug
- current framework status
- module boundaries
- naming conventions
- route/menu/permission expectations
- verification commands
- files future Agents should read first

## 4. Configuration Targets

When applying a manifest to the repo, update only the smallest necessary set.

Recommended targets:

- `.env.example`
  - add project naming variables when the runtime supports them
- `src/config/frameworkConfig.ts`
  - update `FRAMEWORK_DEFAULT_ROUTE`
  - update enabled/planned module list
- `src/stores/system/systemConfig.ts`
  - update frontend default system name fallback
- `src/router/index.ts`
  - update document title fallback if project name is hardcoded there
- `src/views/LoginView.vue`
  - update visible fallback app name if hardcoded
- `src/views/HomeView.vue`
  - update visible fallback app name if hardcoded
- `src/layouts/BaseLayout.vue`
  - update visible fallback app name if hardcoded
- `src/layouts/MainLayout.vue`
  - update visible fallback app name if hardcoded
- `backend/main.py`
  - update FastAPI `title` and `description`
- `backend/app/bootstrap/init_db_seed_system.py`
  - update default company and system name seed

If the project already supports env-driven naming, prefer env updates over scattered source edits.

## 5. Suggested Starter Script Contract

When adding a repo-local starter script, use:

```text
scripts/start_project.py
```

Recommended commands:

```bash
./backend/.venv/bin/python scripts/start_project.py --config project.manifest.yaml
./backend/.venv/bin/python scripts/start_project.py --requirements docs/input-requirements.md
./backend/.venv/bin/python scripts/start_project.py --app-name "服务管理系统" --app-slug service_ops --company-name "示例企业"
```

The script should:

1. Load requirements or explicit config.
2. Generate or update `project.manifest.yaml`.
3. Generate `docs/requirements.md`.
4. Generate `docs/agent-brief.md`.
5. Apply project naming fallbacks.
6. Apply framework module plan.
7. Print validation commands.

Keep module generation separate from project start in the first version. After project configuration is stable, use `scripts/scaffold_fullstack_module.py` for real modules.

## 6. Validation

After project-start changes, run at least:

```bash
python3 -m py_compile backend/main.py
npm run type-check
```

When shared framework wiring changed, run:

```bash
bash scripts/verify_framework_baseline.sh
```

Manual smoke:

1. Login page shows expected project name.
2. Browser title uses expected project name.
3. Home page shows expected project name.
4. Enabled module list matches manifest.
5. Backend OpenAPI title and description match manifest.

## 7. Agent Output

Report:

- input mode used
- extracted or provided project fields
- generated files
- changed configuration files
- validation commands and results
- open questions
- recommended next module scaffold command
