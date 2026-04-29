from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system.deps import SystemConfigRouterDeps
from app.modules.system.routes.system_config_routes import register_system_config_routes


def create_system_config_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
) -> APIRouter:
  router = APIRouter(tags=['系统与认证'])
  deps = SystemConfigRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
  )
  register_system_config_routes(router, deps)
  return router
