from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.customer.deps import CustomerRouterDeps
from app.modules.customer.routes.customer_routes import register_customer_routes


def create_customer_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
) -> APIRouter:
  router = APIRouter(tags=['客户管理'])
  deps = CustomerRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
  )
  register_customer_routes(router, deps)
  return router
