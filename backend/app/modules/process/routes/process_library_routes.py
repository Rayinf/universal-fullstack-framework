from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.modules.process.deps import ProcessLibraryRouterDeps
from app.modules.process.services.process_library_query_service import list_process_library, query_process_library_page


def register_process_library_routes(router: APIRouter, deps: ProcessLibraryRouterDeps) -> None:
  @router.get('/manage/api/processLibrary/page')
  def page_process_library(current: int = 1, size: int = 100, keyword: str | None = None) -> dict[str, Any]:
    return deps.ok_func(
      query_process_library_page(
        deps,
        current=current,
        size=size,
        keyword=keyword,
      ),
      'success',
    )

  @router.get('/manage/api/processLibrary/list')
  def list_process_library_records() -> dict[str, Any]:
    return deps.ok_func(list_process_library(deps), 'success')
