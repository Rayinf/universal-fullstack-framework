# API Contract Playbook

## 1) Frontend-first inventory

Extract API matrix from `src/api/**` with:

```bash
rg -n "request\\.(get|post|put|delete)" src/api
```

Capture for each endpoint:

- Method
- Path
- Request payload/query fields
- Expected response shape
- Consuming pages/stores

## 2) Compatibility rules

- Keep path compatibility first; avoid broad frontend rewrites.
- Keep response wrapper stable: `code`, `msg`, `data`.
- Accept both snake_case and camelCase for key auth transition fields when migrating.

## 3) Minimal backend implementation sequence

1. Auth: login, refresh, user-info.
2. Menu and permission baseline.
3. System-management list/detail endpoints.
4. Baseline CRUD endpoints.
5. Remaining non-critical endpoints.

## 4) Retry and error-handling rules

- Retry only network failures, HTTP 429, and HTTP 5xx.
- Do not retry deterministic 4xx errors (404/400/401/403).
- Surface clear user message and log raw error for debugging.

## 5) Production hardening checklist

- `MES_ENV=production` (or equivalent env).
- Strong JWT secret configured.
- CORS whitelist configured and wildcard disabled.
- Access/refresh expiry configured.
- Build + smoke tests pass.
