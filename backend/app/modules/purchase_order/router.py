from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request

from app.modules.purchase_order.deps import PurchaseOrderRouterDeps
from app.modules.purchase_order.routes.purchase_order_routes import register_purchase_order_routes


def create_purchase_order_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
  safe_float_func: Callable[[Any, float], float],
  get_current_user_func: Callable[[Request], Any],
) -> APIRouter:
  router = APIRouter(tags=['本地示例采购'])
  deps = PurchaseOrderRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
    safe_float_func=safe_float_func,
    get_current_user_func=get_current_user_func,
  )
  register_purchase_order_routes(router, deps)
  return router
