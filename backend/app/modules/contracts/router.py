from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request

from app.modules.contracts.deps import ContractRouterDeps
from app.modules.contracts.routes.commission_routes import register_commission_routes
from app.modules.contracts.routes.contract_routes import register_contract_routes
from app.modules.contracts.routes.payment_routes import register_payment_routes


def create_contract_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
  safe_float_func: Callable[[Any, float], float],
  get_current_user_func: Callable[[Request], Any],
  export_to_excel_func: Callable[[list[str], list[list[Any]], str], Any],
  create_notification_for_users_func: Callable[..., None],
) -> APIRouter:
  router = APIRouter(tags=['本地示例合同回款佣金'])
  deps = ContractRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
    safe_float_func=safe_float_func,
    get_current_user_func=get_current_user_func,
    export_to_excel_func=export_to_excel_func,
    create_notification_for_users_func=create_notification_for_users_func,
  )
  register_contract_routes(router, deps)
  register_payment_routes(router, deps)
  register_commission_routes(router, deps)
  return router
