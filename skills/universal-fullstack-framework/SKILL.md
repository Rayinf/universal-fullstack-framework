---
name: universal-fullstack-framework
description: End-to-end workflow for building or refactoring a generic business web system into a reusable fullstack framework using Vue 3 + TypeScript frontend and Python FastAPI backend, then extending business modules on top of that framework. Use when you need to retain only core system-management capabilities, replace remote or mock APIs with local backend implementations, scaffold standard CRUD pages, keep frontend design standards consistent, align route/menu/API contracts, fix frontend-backend integration errors (404, redirect loop, import/HMR failures), and harden auth/JWT/CORS for production deployment.
---

# Universal Fullstack Framework

## Overview

Use this skill to transform an existing business system into a reusable development framework that supports incremental feature modules on top of a stable core.

Prioritize a stable foundation first: authentication, system management, configuration, user-role-permission, logs, backup, and one baseline CRUD capability.

After the core is stable, use the same workflow to build new business modules in small, reversible increments without breaking shared frontend patterns.

## Workflow

### 1) Freeze scope and protect the core

- Keep only core management capabilities and one baseline CRUD module.
- Disable or remove unrelated business modules from router, menu, and navigation guards.
- Keep a single home entry and avoid duplicate dashboard/home menu items.

### 2) Establish frontend-backend contract first

- Inventory all frontend API calls under `src/api/**`.
- Map each call to backend route, method, and payload fields.
- For unimplemented endpoints, choose one strategy:
  - Implement the backend endpoint.
  - Redirect frontend call to an existing equivalent endpoint.
  - Temporarily disable non-critical call sites.
- Prefer contract compatibility over large frontend rewrites.

For endpoint contract templates and naming conventions, read `references/api-contract-playbook.md`.

### 3) Replace remote or mock dependencies with local Python backend

- Use FastAPI as local backend with explicit modular endpoints.
- Add PostgreSQL seed data (or equivalent relational seed data) for management pages and CRUD demos.
- Keep response schema consistent:
  - success: `{ code: 0|200, msg, data }`
  - failure: `{ code: non-0, msg, data: null }`
- Keep ID fields as string for frontend consistency.

### 4) Build baseline frontend pattern

- Use unified request wrapper and centralized error handling.
- Add one complete CRUD page template: list, search, pagination, create, update, delete.
- Keep store pattern consistent (Pinia composition-style).
- Reuse dialog/form/table patterns from existing system pages.

For UI consistency rules, read `references/frontend-design-standard.md`.

### 5) Resolve integration faults systematically

- For 404 storms, verify endpoint path and prefix mapping first.
- For retry floods, retry only network errors, 429, and 5xx; do not retry fixed 4xx.
- For route guard loops, verify redirect base case and auth-state initialization.
- For dynamic import/style 500, verify file path, alias, and preprocessor dependencies.
- For HMR failures, clear syntax/import/runtime errors first, then check Vite config.

### 6) Harden auth and production configuration

- Use password hash verification (for example PBKDF2), not plaintext compare.
- Use JWT access + refresh tokens with token-type validation.
- Support request-field compatibility for refresh token (`refresh_token` and `refreshToken`) when needed.
- Make CORS environment-driven and enforce production fail-fast checks:
  - Require strong JWT secret.
  - Reject wildcard CORS in production.
  - Require explicit origin list or regex.

### 7) Validate each iteration

Run at least:

```bash
python3 -m py_compile backend/main.py
npm run type-check
npm run build-only
```

- If the repo contains `scripts/verify_framework_baseline.sh`, prefer running that script after baseline-affecting changes instead of manually reassembling the command set each time.
- Treat `scripts/verify_framework_baseline.sh` as the default local gate for:
  - backend route/service/repository changes
  - scaffold changes
  - registry changes
  - frontend router/menu/request/build changes

Run a smoke flow after each core change:

1. Login.
2. Access protected user-info API.
3. Access one management list API.
4. Refresh token.
5. Open CRUD page and execute create/update/delete.

### 8) Extend modules on top of the framework

- Add a new module by sequence: route -> menu -> page scaffold -> API -> store -> type definitions.
- Implement one smallest usable flow first (usually list + detail or list + CRUD).
- Reuse shared layout and components before creating new component variants.
- Keep extension code isolated in module directories and avoid changes to core auth/request/router logic unless necessary.
- Validate each new module with the same smoke and build checks before moving to the next.

### 8A) Prefer repo-local backend scaffolds when available

- If the current repo contains `backend/scripts/scaffold_backend_module.py` and `backend/app/modules/_template/`, use that scaffold first instead of hand-copying module skeletons.
- Example:

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py quality_report \
  --tag "质检报告" \
  --resource-path /manage/api/qualityReport \
  --table-name quality_report_records
```

- After scaffold generation, immediately:
  - Replace placeholder route paths, table names, labels, and error messages with real business values.
  - Confirm the scaffold also registered the new router in `backend/app/bootstrap/scaffold_router_registry.py`.
  - Add or update targeted tests in `backend/tests/`.
  - Run `py_compile` for the generated module and then run targeted + full backend tests.
- For parameter details and generated file layout, read `backend/docs/backend-module-template.md`.
- Do not leave generated `/example` endpoints, `example_table`, or placeholder service logic in final code.

### 8B) Prefer repo-local frontend scaffolds and registries when available

- If the current repo contains `scripts/scaffold_frontend_module.py` and `scaffolds/frontend_module/`, use that scaffold first instead of hand-copying `types/api/view/store`.
- Prefer writing generated route and menu entries into registry files such as:
  - `src/router/scaffoldedRoutes.ts`
  - `src/config/scaffoldMenuRegistry.ts`
  - `backend/app/modules/system_admin/scaffold_menu_registry.py`
- Keep `src/router/index.ts`, `src/config/menuConfig.ts`, and `backend/app/modules/system_admin/menu.py` as stable aggregation layers; do not keep appending one-off business entries directly into those main files when the registry mechanism exists.
- Example:

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --menu-parent system \
  --route-path /system/quality-report \
  --route-name system-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

- After scaffold generation, immediately:
  - Replace placeholder query fields, table columns, form items, validation rules, and error messages with real business definitions.
  - Confirm generated route/menu registration matches the intended module bucket (`root/system/sales/production`).
  - Confirm `backend/app/modules/system_admin/scaffold_menu_registry.py` also received the matching backend menu entry.
  - Sync frontend `meta.functionCode` and backend `permission` code together.
  - Add or update targeted tests in `backend/tests/test_frontend_scaffold.py` if the scaffold behavior changes.
  - Run `python3 -m py_compile scripts/scaffold_frontend_module.py backend/tests/test_frontend_scaffold.py`, `python3 -m unittest backend.tests.test_frontend_scaffold -v`, and `npm run type-check`.
- For parameter details and generated file layout, read `docs/frontend-module-template.md`.
- Do not leave generated placeholder fields (`name/code/status/remark`) as final business schema.

### 8C) Prefer the repo-local fullstack scaffold as the default entry when both sides change

- If the current repo contains `scripts/scaffold_fullstack_module.py`, use it as the first choice when a new module needs both backend endpoints and frontend page/menu/route wiring in the same turn.
- Example:

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

- Treat this script as a thin orchestrator, not a new template system:
  - it should reuse `backend/scripts/scaffold_backend_module.py`
  - it should reuse `scripts/scaffold_frontend_module.py`
  - it should write through existing registries instead of appending entries directly into large main files
- Prefer it for standard CRUD-style module creation because it should automatically cover:
  - backend module generation
  - backend router registry
  - frontend `types/api/view/store`
  - frontend route registry
  - frontend menu registry
  - backend menu registry
- Fall back to `8A` or `8B` only when the task is intentionally single-sided or needs nonstandard output paths/registration behavior.
- After scaffold generation, immediately:
  - Replace placeholder fields, labels, table names, and SQL with real business definitions.
  - Confirm `menu_parent`, generated frontend directories, and route path all belong to the same module bucket.
  - Confirm frontend `meta.functionCode` and backend `permission` are still identical.
  - Run `python3 -m py_compile scripts/scaffold_fullstack_module.py backend/tests/test_fullstack_scaffold.py`, `backend/.venv/bin/python -m unittest backend.tests.test_fullstack_scaffold -v`, and then `npm run type-check` if generated files landed in the real repo.
  - If the repo contains `scripts/verify_framework_baseline.sh`, run it before closing the task when the scaffold change or generated module touched shared framework wiring.
- For parameter details and the recommended workflow, read `docs/fullstack-module-template.md`.

### 8D) Keep repo-local CI and local verify entry aligned

- If the repo contains both `.github/workflows/ci.yml` and `scripts/verify_framework_baseline.sh`, keep them functionally aligned.
- When adding a new mandatory validation step for the framework:
  - update the local verify script
  - update CI
  - update the corresponding doc, such as `docs/ci-baseline.md`
- Prefer a small number of stable checks over many fragile jobs; the goal is a dependable baseline gate, not exhaustive infrastructure.

## Output standard

When completing tasks with this skill, report:

- Changed files grouped by backend/frontend/config.
- Resolved error categories (404, redirect loop, import 500, auth failure, etc.).
- Validation commands and pass/fail results.
- Remaining risks and next hardening steps.

## Recent pitfalls and guardrails

Add these checks as default guardrails when applying this skill:

### A) Route-menu-permission-layout must move together

When moving or adding module paths (for example `/sales/*`, `/production/*`), always update all of:

1. Frontend router entry (`src/router/scaffoldedRoutes.ts` or `src/router/index.ts`)
2. Frontend menu entry (`src/config/scaffoldMenuRegistry.ts` or `src/config/menuConfig.ts`)
3. Backend menu entry (`backend/app/modules/system_admin/scaffold_menu_registry.py` or `backend/app/modules/system_admin/menu.py`)
4. Layout/menu filtering and route-guard allowlist (`src/layouts/MainLayout.vue`, `src/config/frameworkConfig.ts`, menu store helpers)

If any one of these is missed, the symptom is usually "menu still appears under old group" or "menu not visible at all".

### B) Verify role-menu mapping after menu-tree changes

- Ensure `role_menus` defaults are regenerated from latest flattened `menu_tree()` IDs.
- Verify both endpoints after login:
  - `/admin/menu/tree`
  - `/admin/menu/tree/{roleId}`
- If tree is correct but UI is wrong, inspect frontend filtering first.

### C) Seed data must be end-to-end, not isolated

- Keep seed insertion in `init_db()` using empty-table checks.
- Seed complete business chains so new pages are testable immediately:
  - product -> quotation -> contract -> payment -> commission
  - work order -> work report -> work inbound
- Avoid frontend-only mock patches for integration scenarios.

### D) UI consistency belongs in shared styles

- New module pages must import shared common styles.
- Shared table container spacing (desktop/mobile) should live in `src/styles/common.css`.
- Do not keep critical spacing rules only in old demo pages.

### E) Environment and dependency sanity checks

- For `UploadFile`/`Form`, ensure `python-multipart` is installed in the project virtualenv.
- Install dependencies with the virtualenv interpreter, not global Python.
- Treat `Address already in use` as port/process conflict, not code regression.

### F) Recommended incremental verification

In addition to compile/type/build, run these quick checks after navigation or module moves:

1. Re-login and hard refresh.
2. Confirm top-level menu grouping and access paths.
3. Open one list page per module and verify pagination/action buttons.
4. Validate one export/download action and one notification jump path.

## Minimal universal guardrails (must keep)

Use these as the default high-signal rules for agent execution across projects.

1. Change-closure checklist

- For any feature/module move, verify in order:
  - route
  - menu
  - permission/function code
  - guard/filter/allowlist
  - API contract and UI entry

2. Contract-first implementation

- Define endpoint contract before coding:
  - path, method, request fields, response schema, error codes, compatibility fields
- Prefer backend compatibility adapters over large frontend rewrites.

3. Environment consistency

- Install and run dependencies inside the project runtime (venv/workspace), not global runtime.
- For runtime errors around missing packages, verify interpreter path first.

4. Shared-style governance

- Put cross-page style rules in shared style files.
- Keep page-local styles only for intentional page-specific differences.

5. Iteration gate (minimum)

- Require all before moving forward:
  - `python3 -m py_compile backend/main.py` (or project-equivalent compile check)
  - `npm run type-check` (or frontend-equivalent type check)
  - `npm run build-only` (or project-equivalent build)
  - one smoke flow for login + protected API + one CRUD create/update/delete
