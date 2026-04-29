#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-"$ROOT_DIR/backend/.venv/bin/python"}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "未找到可执行 Python: $PYTHON_BIN" >&2
  echo "可通过 PYTHON_BIN=/path/to/python 覆盖" >&2
  exit 1
fi

cd "$ROOT_DIR"

echo "[1/5] Python 编译检查"
"$PYTHON_BIN" -m py_compile \
  backend/main.py \
  backend/scripts/scaffold_backend_module.py \
  scripts/scaffold_frontend_module.py \
  scripts/scaffold_fullstack_module.py \
  backend/tests/test_backend_scaffold.py \
  backend/tests/test_frontend_scaffold.py \
  backend/tests/test_fullstack_scaffold.py \
  backend/tests/test_http_smoke.py \
  backend/tests/test_menu_registry.py \
  backend/tests/test_router_registry.py

echo "[2/5] 后端基座回归"
"$PYTHON_BIN" -m unittest \
  backend.tests.test_frontend_scaffold \
  backend.tests.test_menu_registry \
  backend.tests.test_modular_routes \
  backend.tests.test_backend_scaffold \
  backend.tests.test_router_registry \
  backend.tests.test_fullstack_scaffold \
  -v

echo "[3/5] PostgreSQL HTTP smoke"
"$PYTHON_BIN" -m unittest backend.tests.test_http_smoke -v

echo "[4/5] 前端类型检查"
npm run type-check

echo "[5/5] 前端构建检查"
npm run build-only

echo "BASELINE_VERIFY_OK"
