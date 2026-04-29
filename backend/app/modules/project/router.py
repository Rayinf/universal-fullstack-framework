from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.project.deps import ProjectRouterDeps
from app.modules.project.routes.project_routes import register_project_routes


def create_project_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
) -> APIRouter:
  router = APIRouter(tags=['本地示例项目'])
  deps = ProjectRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
  )
  register_project_routes(router, deps)
  return router
