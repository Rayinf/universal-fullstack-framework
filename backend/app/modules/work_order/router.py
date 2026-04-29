from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request

from app.modules.work_order.deps import WorkOrderRouterDeps
from app.modules.work_order.routes.work_inbound_routes import register_work_inbound_routes
from app.modules.work_order.routes.work_order_routes import register_work_order_routes
from app.modules.work_order.routes.work_report_routes import register_work_report_routes


def create_work_order_router(
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
  router = APIRouter(tags=['本地示例生产闭环'])
  deps = WorkOrderRouterDeps(
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
  register_work_order_routes(router, deps)
  register_work_report_routes(router, deps)
  register_work_inbound_routes(router, deps)
  return router
