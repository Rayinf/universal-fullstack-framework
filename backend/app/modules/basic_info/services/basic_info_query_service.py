from __future__ import annotations

from app.modules.basic_info.deps import BasicInfoRouterDeps
from app.modules.basic_info.helpers import build_basic_info_filters, normalize_pagination
from app.modules.basic_info.repositories.basic_info_repo import (
  query_basic_info_list_rows,
  query_basic_info_list_rows_by_type,
  query_basic_info_page_rows,
  query_basic_info_page_total,
)
from app.modules.basic_info.serializers import basic_info_to_dict, build_page_result


def query_basic_info_page(
  deps: BasicInfoRouterDeps,
  *,
  page: int | None,
  current: int | None,
  size: int,
  info_type: int | None,
  key_word: str | None,
) -> dict[str, object]:
  page_current, page_size = normalize_pagination(page, current, size)
  where_sql, values = build_basic_info_filters(info_type, key_word)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  total = int(query_basic_info_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_basic_info_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  conn.close()
  return build_page_result([basic_info_to_dict(row) for row in rows], total, page_current, page_size)


def list_basic_info(deps: BasicInfoRouterDeps, *, info_type: int | None) -> list[dict[str, object]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  if info_type is None:
    rows = query_basic_info_list_rows(cur)
  else:
    rows = query_basic_info_list_rows_by_type(cur, int(info_type))
  conn.close()
  return [basic_info_to_dict(row) for row in rows]
