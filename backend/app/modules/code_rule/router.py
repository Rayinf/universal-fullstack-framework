from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.code_rule.deps import CodeRuleRouterDeps
from app.modules.code_rule.routes.code_rule_routes import register_code_rule_routes


def create_code_rule_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
) -> APIRouter:
  router = APIRouter(tags=['编码规则'])
  deps = CodeRuleRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
  )
  register_code_rule_routes(router, deps)
  return router
