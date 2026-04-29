from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.system.deps import AuthRouterDeps
from app.modules.system.routes.auth_routes import register_auth_routes

def create_auth_router(
  fail_func: Callable[[str, int], Any],
  ok_func: Callable[[Any, str], dict[str, Any]],
  get_conn_func: Callable[[], Any],
  verify_password_func: Callable[[str, str], bool],
  build_token_func: Callable[[str, str, int], str],
  parse_token_func: Callable[..., dict[str, Any] | None],
  access_token_expire_seconds: int,
  refresh_token_expire_seconds: int,
) -> APIRouter:
  router = APIRouter(tags=['系统与认证'])
  deps = AuthRouterDeps(
    fail_func=fail_func,
    ok_func=ok_func,
    get_conn_func=get_conn_func,
    verify_password_func=verify_password_func,
    build_token_func=build_token_func,
    parse_token_func=parse_token_func,
    access_token_expire_seconds=access_token_expire_seconds,
    refresh_token_expire_seconds=refresh_token_expire_seconds,
  )
  register_auth_routes(router, deps)
  return router
