from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system.deps import SystemRouterDeps
from app.modules.system.routes.system_routes import register_system_routes


def create_system_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  db_driver: str,
) -> APIRouter:
  router = APIRouter(tags=['系统与认证'])
  deps = SystemRouterDeps(ok_func=ok_func, db_driver=db_driver)
  register_system_routes(router, deps)
  return router
