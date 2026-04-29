from __future__ import annotations

from typing import Any

from app.modules.local_crud.deps import LocalCrudRouterDeps
from app.modules.local_crud.helpers import build_keyword_filter
from app.modules.local_crud.repositories.crud_item_repo import (
  query_crud_item_page_rows,
  query_crud_item_page_total,
)
from app.modules.local_crud.serializers import build_page_result, crud_item_to_dict


def query_crud_item_page(
  deps: LocalCrudRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  keyword_sql, keyword_values = build_keyword_filter(keyword)
  where_sql += keyword_sql
  values.extend(keyword_values)

  total = int(query_crud_item_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_crud_item_page_rows(cur, where_sql, tuple(values), size, (current - 1) * size)
  conn.close()
  return build_page_result([crud_item_to_dict(row) for row in rows], total, current, size)
