from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.local_crud.deps import LocalCrudRouterDeps
from app.modules.local_crud.routes.local_crud_routes import register_local_crud_routes


def create_local_crud_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
) -> APIRouter:
  router = APIRouter(tags=['本地示例 CRUD'])
  deps = LocalCrudRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
  )
  register_local_crud_routes(router, deps)
  return router
