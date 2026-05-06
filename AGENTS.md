# AGENTS.md - AI Coding Guide

This file gives AI coding assistants a stable working contract for this repository.

## 1. Project Overview

This repository is a reusable fullstack framework for enterprise management systems. It combines:

- Vue 3 + TypeScript + Vite frontend
- Element Plus UI components
- Pinia state management
- Vue Router navigation and guards
- Axios-based request wrapper
- Python FastAPI backend
- PostgreSQL persistence
- Scaffold scripts for backend, frontend, and fullstack CRUD modules
- A packaged Agent Skill under `skills/universal-fullstack-framework/`

The repository includes several example business domains to demonstrate how modules attach to the shared foundation. Treat those domains as samples for extension patterns. The framework core is authentication, user/role/menu/permission management, system configuration, logs, backups, baseline CRUD, route/menu/permission registries, and validation scripts.

## 2. Build, Test, And Run Commands

### Development

```bash
npm run dev              # Start frontend dev server
npm run dev:local        # Start frontend dev server on localhost only
npm run backend:dev      # Start FastAPI backend with PostgreSQL defaults
npm run backend:dev:pg   # Explicit PostgreSQL backend startup
npm run build            # Type-check plus production build
npm run preview          # Preview production build
```

### Quality

```bash
npm run lint             # ESLint check and auto-fix
npm run format           # Prettier format for src/
npm run type-check       # Vue TypeScript check
```

### Tests

```bash
npm run test:unit
vitest run <file>
vitest run -t "test name"
```

### Baseline Gate

Use the repository-level baseline gate for framework, scaffold, router, menu, backend, or auth changes:

```bash
bash scripts/verify_framework_baseline.sh
```

The script runs Python compile checks, backend regression tests, HTTP smoke tests, frontend type-check, and production build.

## 3. Framework Boundaries

Preserve the shared framework foundation:

- authentication and token storage
- request wrapper and API response normalization
- route guards
- menu and permission registries
- shared layout components
- common dialog/form/table patterns
- scaffold scripts and templates
- `scripts/verify_framework_baseline.sh`

When adding business functionality, keep extension code isolated under module-oriented directories:

- `backend/app/modules/<domain>/`
- `src/api/<bucket>/`
- `src/types/<bucket>/`
- `src/stores/<bucket>/`
- `src/views/<view-bucket>/`

## 4. Scaffold Workflow

Prefer the repo-local fullstack scaffold when both backend and frontend are involved:

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py example_record \
  --tag "Example Record" \
  --api-base-path /manage/api/exampleRecord \
  --table-name example_records \
  --menu-parent system \
  --route-path /system/example-record \
  --route-name system-example-record \
  --function-code APP-FUNC-EXAMPLE-RECORD \
  --with-store
```

After generation:

1. Replace placeholder fields such as `name`, `code`, `status`, and `remark`.
2. Replace placeholder labels, columns, forms, validation rules, SQL, and error messages.
3. Confirm frontend `meta.functionCode` matches backend `permission`.
4. Confirm route path, menu parent, backend menu entry, and layout filtering agree.
5. Run targeted scaffold tests and the baseline gate.

Use single-sided scaffolds only for intentionally single-sided work:

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py <module_name>
./backend/.venv/bin/python scripts/scaffold_frontend_module.py <module_name>
```

## 5. Route, Menu, Permission, Layout Alignment

Route/menu/permission/layout must move together. For any new page or path change, check:

1. Frontend route registry: `src/router/scaffoldedRoutes.ts` or `src/router/index.ts`
2. Frontend menu registry: `src/config/scaffoldMenuRegistry.ts` or `src/config/menuConfig.ts`
3. Backend menu registry: `backend/app/modules/system_admin/scaffold_menu_registry.py` or `backend/app/modules/system_admin/menu.py`
4. Layout and guard allowlist: `src/layouts/MainLayout.vue`, `src/config/frameworkConfig.ts`, menu store helpers

Also verify:

- frontend `meta.functionCode`
- backend `permission`
- role-menu default mappings
- `/admin/menu/tree`
- `/admin/menu/tree/{roleId}`

## 6. Frontend Coding Standards

### Imports

Recommended order:

1. Vue core
2. third-party libraries
3. local types
4. local API modules
5. local stores
6. local components
7. local utilities
8. local composables

Use `@/` aliases for source imports.

### TypeScript

Use explicit types for refs, state, API payloads, and table rows.

```typescript
const records = ref<RecordItem[]>([])
const loading = ref<boolean>(false)
const total = ref<number>(0)
```

Use `interface` for structured data unless a union or mapped type is needed. Keep ID fields as `string` for frontend/backend consistency.

### Vue

Use `<script setup lang="ts">` and Composition API. Keep component order:

```vue
<template>
<script setup lang="ts">
<style scoped>
```

### Pinia

Prefer Composition-style stores:

```typescript
export const useExampleStore = defineStore('example', () => {
  const records = ref<ExampleRecord[]>([])
  const loading = ref(false)

  const fetchRecords = async () => {
    loading.value = true
    try {
      // API call
    } finally {
      loading.value = false
    }
  }

  return { records, loading, fetchRecords }
})
```

### API

Use `src/utils/request.ts`:

```typescript
const result = await request.get<ResponseType>('/api/path', params)
const saved = await request.post<ResponseType>('/api/path', payload)
```

Treat `code === 0` and `code === 200` as success.

## 7. Backend Coding Standards

Backend modules should follow this structure:

```text
backend/app/modules/<domain>/
├── router.py
├── deps.py
├── helpers.py
├── serializers.py
├── routes/
├── services/
└── repositories/
```

Layer responsibilities:

- `router.py`: create and register routes
- `deps.py`: collect route dependencies
- `helpers.py`: parse and normalize inputs
- `serializers.py`: map rows to API response structures
- `routes/`: read HTTP inputs and call services
- `services/`: coordinate business logic and transactions
- `repositories/`: own SQL

Keep response shape consistent:

```json
{ "code": 0, "msg": "success", "data": {} }
```

## 8. Error Handling

All async frontend operations need full loading and error handling:

```typescript
const fetchData = async () => {
  loading.value = true
  try {
    const res = await api()
    if (res.code === 0 || res.code === 200) {
      records.value = res.data || []
    } else {
      ElMessage.error(res.msg || 'Operation failed')
    }
  } catch (error) {
    console.error('Fetch failed:', error)
    ElMessage.error('Network error')
  } finally {
    loading.value = false
  }
}
```

## 9. Shared UI Standards

- Use `ElMessage` for lightweight feedback.
- Use `ElMessageBox.confirm` for destructive operations.
- Use form `:rules` for validation.
- Use striped and highlightable tables.
- Import shared page styles with `@import '@/styles/common.css'`.
- Put shared table/container spacing in `src/styles/common.css`.
- Keep new module pages visually aligned with existing scaffold pages.

## 10. Constants And Pagination

Use `src/utils/constants.ts`:

```typescript
export const PAGE_SIZE_CONFIG = {
  LARGE_PAGE_SIZE: 100000,
  DEFAULT_PAGE_SIZE: 20,
  SMALL_PAGE_SIZE: 10,
} as const
```

Default list pages use normal pagination. Selector APIs can request large page sizes when necessary.

## 11. Seed Data

Seed data should live in backend initialization code and use empty-table checks:

```sql
SELECT COUNT(1) AS cnt FROM table_name
```

Provide complete demo chains for example domains so pages are testable immediately. Prefer backend seed data over frontend-only mocks for integration scenarios.

## 12. Git Commit Convention

Use conventional commits:

- `feat:`
- `fix:`
- `docs:`
- `style:`
- `refactor:`
- `test:`
- `chore:`

## 13. Validation Checklist

Before closing framework or module work, run or report:

- `python3 -m py_compile backend/main.py`
- targeted backend tests when backend changed
- `npm run type-check`
- `npm run build-only`
- `bash scripts/verify_framework_baseline.sh` for shared framework changes

Manual smoke:

1. Login.
2. Open protected user info.
3. Open menu tree.
4. Open one list page.
5. Create, update, delete one demo record when the module supports CRUD.

## 14. Related Docs

- `README.md`
- `FRAMEWORK_GUIDE.md`
- `docs/fullstack-module-template.md`
- `docs/frontend-module-template.md`
- `backend/docs/backend-module-template.md`
- `skills/universal-fullstack-framework/SKILL.md`
