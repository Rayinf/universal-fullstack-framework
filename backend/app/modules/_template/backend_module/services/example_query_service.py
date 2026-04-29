from __future__ import annotations

from app.modules._template.backend_module.deps import ExampleRouterDeps
from app.modules._template.backend_module.helpers import normalize_page_args
from app.modules._template.backend_module.repositories.example_repo import (
  query_example_page_rows,
  query_example_page_total,
)
from app.modules._template.backend_module.serializers import build_page_result


def query_example_page(
  deps: ExampleRouterDeps,
  *,
  current: int,
  size: int,
) -> dict[str, object]:
  page_current, page_size = normalize_page_args(current, size)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  total_row = query_example_page_total(cur)
  rows = query_example_page_rows(cur, size=page_size, offset=(page_current - 1) * page_size)
  conn.close()
  total = int(total_row['cnt']) if total_row else 0
  return build_page_result(rows, total, page_current, page_size)
