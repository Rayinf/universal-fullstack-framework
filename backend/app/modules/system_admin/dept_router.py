from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system_admin.deps import DeptReadRouterDeps
from app.modules.system_admin.routes.dept_read_routes import register_dept_read_routes


def create_dept_read_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  build_dept_tree_func: Callable[..., list[dict[str, Any]]],
) -> APIRouter:
  router = APIRouter(tags=['组织与用户'])
  deps = DeptReadRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    build_dept_tree_func=build_dept_tree_func,
  )
  register_dept_read_routes(router, deps)
  return router
