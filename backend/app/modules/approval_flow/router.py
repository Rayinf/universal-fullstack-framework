from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.routes.approval_flow_result_routes import register_approval_flow_result_routes
from app.modules.approval_flow.routes.approval_flow_routes import register_approval_flow_routes


def create_approval_flow_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
  get_process_library_records_func: Callable[[], list[dict[str, Any]]],
) -> APIRouter:
  router = APIRouter(tags=['审批流'])
  deps = ApprovalFlowRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
    get_process_library_records_func=get_process_library_records_func,
  )
  register_approval_flow_routes(router, deps)
  register_approval_flow_result_routes(router, deps)
  return router
