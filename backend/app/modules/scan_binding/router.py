from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.scan_binding.deps import ScanBindingRouterDeps
from app.modules.scan_binding.routes.scan_binding_routes import register_scan_binding_routes


def create_scan_binding_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
) -> APIRouter:
  router = APIRouter(tags=['扫码绑定工序'])
  deps = ScanBindingRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
  )
  register_scan_binding_routes(router, deps)
  return router
