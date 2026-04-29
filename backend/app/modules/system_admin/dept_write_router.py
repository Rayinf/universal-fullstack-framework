from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system_admin.deps import DeptWriteRouterDeps
from app.modules.system_admin.routes.dept_write_routes import register_dept_write_routes


def create_dept_write_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  safe_int_func: Callable[[Any, int], int],
  now_str_func: Callable[[], str],
  collect_descendant_ids_func: Callable[[str, list[Any]], set[str]],
) -> APIRouter:
  router = APIRouter(tags=['组织与用户'])
  deps = DeptWriteRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    safe_int_func=safe_int_func,
    now_str_func=now_str_func,
    collect_descendant_ids_func=collect_descendant_ids_func,
  )
  register_dept_write_routes(router, deps)
  return router
