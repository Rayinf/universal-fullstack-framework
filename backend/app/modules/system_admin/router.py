from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system_admin.deps import SystemAdminRouterDeps
from app.modules.system_admin.routes.system_admin_routes import register_system_admin_routes


def create_system_admin_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  get_conn_func: Callable[[], Any],
  menu_tree_func: Callable[[], list[dict[str, Any]]],
) -> APIRouter:
  router = APIRouter(tags=['菜单与权限'])
  deps = SystemAdminRouterDeps(
    ok_func=ok_func,
    get_conn_func=get_conn_func,
    menu_tree_func=menu_tree_func,
  )
  register_system_admin_routes(router, deps)
  return router
