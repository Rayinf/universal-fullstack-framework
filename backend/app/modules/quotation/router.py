from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request

from app.modules.quotation.deps import QuotationRouterDeps
from app.modules.quotation.routes.quotation_routes import register_quotation_routes


def create_quotation_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
  safe_float_func: Callable[[Any, float], float],
  get_current_user_func: Callable[[Request], Any],
  create_notification_for_users_func: Callable[..., None],
) -> APIRouter:
  router = APIRouter(tags=['本地示例报价'])
  deps = QuotationRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
    safe_float_func=safe_float_func,
    get_current_user_func=get_current_user_func,
    create_notification_for_users_func=create_notification_for_users_func,
  )
  register_quotation_routes(router, deps)
  return router
