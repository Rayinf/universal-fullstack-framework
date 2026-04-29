from __future__ import annotations

from typing import Any

from app.modules.project.deps import ProjectRouterDeps
from app.modules.project.helpers import build_project_page_filters
from app.modules.project.repositories.project_repo import query_project_page_rows, query_project_page_total
from app.modules.project.serializers import build_page_result, project_to_dict


def query_project_page(
  deps: ProjectRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  status: int | None,
) -> dict[str, Any]:
  where_sql, values = build_project_page_filters(keyword, status)
  conn = deps.get_conn_func()
  cur = conn.cursor()
  total = int(query_project_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_project_page_rows(cur, where_sql, tuple(values), size, (current - 1) * size)
  conn.close()
  return build_page_result([project_to_dict(row) for row in rows], total, current, size)
