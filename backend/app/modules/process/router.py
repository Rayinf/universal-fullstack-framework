from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter

from app.modules.process.deps import ProcessLibraryRouterDeps
from app.modules.process.routes.process_library_routes import register_process_library_routes


def get_process_library_records() -> list[dict[str, Any]]:
  return [
    {'id': '1', 'processName': '标准工序', 'isKey': 0, 'processStatus': 1, 'items': []},
    {'id': '2', 'processName': '检验工序', 'isKey': 0, 'processStatus': 1, 'items': []},
  ]


def create_process_library_router(
  ok_func: Callable[[Any, str], dict[str, Any]],
  get_process_library_records_func: Callable[[], list[dict[str, Any]]] = get_process_library_records,
) -> APIRouter:
  router = APIRouter(tags=['工艺库'])
  deps = ProcessLibraryRouterDeps(
    ok_func=ok_func,
    get_process_library_records_func=get_process_library_records_func,
  )
  register_process_library_routes(router, deps)
  return router
