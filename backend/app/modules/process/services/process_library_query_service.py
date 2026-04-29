from __future__ import annotations

from app.modules.process.deps import ProcessLibraryRouterDeps
from app.modules.process.helpers import filter_process_library_records, normalize_page_args, slice_page_records
from app.modules.process.repositories.process_library_repo import list_process_library_records
from app.modules.process.serializers import build_process_library_page


def query_process_library_page(
  deps: ProcessLibraryRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
) -> dict[str, object]:
  static_records = filter_process_library_records(list_process_library_records(deps), keyword)
  page_current, page_size = normalize_page_args(current, size)
  total = len(static_records)
  return build_process_library_page(
    records=slice_page_records(static_records, page_current, page_size),
    total=total,
    current=page_current,
    size=page_size,
  )


def list_process_library(deps: ProcessLibraryRouterDeps) -> list[dict[str, object]]:
  return list_process_library_records(deps)
