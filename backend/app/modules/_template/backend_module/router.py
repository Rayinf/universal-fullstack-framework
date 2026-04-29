from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules._template.backend_module.deps import ExampleRouterDeps
from app.modules._template.backend_module.routes.example_routes import register_example_routes


def create_example_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
) -> APIRouter:
  router = APIRouter(tags=['示例模板模块'])
  deps = ExampleRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
  )
  register_example_routes(router, deps)
  return router
