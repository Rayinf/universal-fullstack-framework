from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.sys_log.deps import SysLogRouterDeps
from app.modules.sys_log.routes.sys_log_routes import register_sys_log_routes


def create_sys_log_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
) -> APIRouter:
  router = APIRouter(tags=['操作日志'])
  deps = SysLogRouterDeps(ok_func=ok_func, fail_func=fail_func, get_conn_func=get_conn_func)
  register_sys_log_routes(router, deps)
  return router
