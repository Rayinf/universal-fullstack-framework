from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.inventory.deps import InventoryRouterDeps
from app.modules.inventory.routes.inventory_routes import register_inventory_routes


def create_inventory_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
  safe_float_func: Callable[[Any, float], float],
) -> APIRouter:
  router = APIRouter(tags=['本地示例库存'])
  deps = InventoryRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
    safe_float_func=safe_float_func,
  )
  register_inventory_routes(router, deps)
  return router
