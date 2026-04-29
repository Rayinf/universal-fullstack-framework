from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.workstation.deps import WorkstationRouterDeps
from app.modules.workstation.routes.workstation_routes import register_workstation_routes

def create_workstation_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  fail_func: Callable[[str, int], Any],
  get_conn_func: Callable[[], Any],
  now_str_func: Callable[[], str],
  safe_int_func: Callable[[Any, int], int],
  load_name_maps_func: Callable[[Any], tuple[dict[str, str], dict[str, str], dict[str, str]]],
) -> APIRouter:
  router = APIRouter(tags=['工位管理'])
  deps = WorkstationRouterDeps(
    ok_func=ok_func,
    fail_func=fail_func,
    get_conn_func=get_conn_func,
    now_str_func=now_str_func,
    safe_int_func=safe_int_func,
    load_name_maps_func=load_name_maps_func,
  )
  register_workstation_routes(router, deps)
  return router
