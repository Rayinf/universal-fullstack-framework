from __future__ import annotations

from app.modules.scan_binding.deps import ScanBindingRouterDeps
from app.modules.scan_binding.helpers import build_scan_binding_where, resolve_page
from app.modules.scan_binding.repositories.scan_binding_repo import (
  query_process_rows,
  query_scan_binding_page_rows,
  query_scan_binding_page_total,
)
from app.modules.scan_binding.serializers import build_scan_binding_page_result, scan_binding_to_dict


def query_scan_binding_page(
  deps: ScanBindingRouterDeps,
  *,
  page: int | None,
  current: int | None,
  size: int,
  keyword: str | None,
) -> dict[str, object]:
  page_current, page_size = resolve_page(current, page, size)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql, values = build_scan_binding_where(keyword)
  total = int(query_scan_binding_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_scan_binding_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  process_map = {int(row['id']): row['name'] for row in query_process_rows(cur)}
  conn.close()
  return build_scan_binding_page_result(
    [scan_binding_to_dict(row, process_map) for row in rows],
    total,
    page_current,
    page_size,
  )
