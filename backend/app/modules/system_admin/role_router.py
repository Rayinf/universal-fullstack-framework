from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system_admin.deps import RoleRouterDeps
from app.modules.system_admin.routes.role_routes import register_role_routes


def create_role_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
) -> APIRouter:
  router = APIRouter(tags=['角色管理'])
  deps = RoleRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
  )
  register_role_routes(router, deps)
  return router
