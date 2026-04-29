from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system_admin.deps import UserRouterDeps
from app.modules.system_admin.routes.user_routes import register_user_routes


def create_user_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  hash_password_func: Callable[[str], str],
  get_current_user_func: Callable[[Request], Any],
) -> APIRouter:
  router = APIRouter(tags=['用户管理'])
  deps = UserRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    hash_password_func=hash_password_func,
    get_current_user_func=get_current_user_func,
  )
  register_user_routes(router, deps)
  return router
