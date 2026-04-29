from __future__ import annotations

from typing import Any

from app.modules.workstation.deps import WorkstationRouterDeps
from app.modules.workstation.helpers import normalize_page_params
from app.modules.workstation.repositories.workstation_repo import (
  fetch_workstation_detail_row,
  query_workstation_list_rows,
  query_workstation_page_rows,
  query_workstation_page_total,
)
from app.modules.workstation.serializers import build_page_result, workstation_to_dict
from app.modules.workstation.services.errors import WorkstationServiceError


def query_workstation_page(
  deps: WorkstationRouterDeps,
  *,
  page: int | None,
  current: int | None,
  size: int,
  keywords: str | None,
  workstation_name: str | None,
  workstation_type: int | None,
  status: int | None,
  dept_id: str | None,
) -> dict[str, Any]:
  page_current, page_size = normalize_page_params(current, page, size)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[Any] = []

  if keywords and keywords.strip():
    where_sql += ' AND (CAST(workstation_no AS TEXT) LIKE ? OR workstation_name LIKE ?)'
    key = f'%{keywords.strip()}%'
    values.extend([key, key])
  if workstation_name and workstation_name.strip():
    where_sql += ' AND workstation_name LIKE ?'
    values.append(f'%{workstation_name.strip()}%')
  if workstation_type is not None:
    where_sql += ' AND workstation_type = ?'
    values.append(int(workstation_type))
  if status is not None:
    where_sql += ' AND status = ?'
    values.append(int(status))
  if dept_id and str(dept_id).strip():
    where_sql += ' AND dept_id = ?'
    values.append(str(dept_id).strip())

  total = int(query_workstation_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_workstation_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  user_map, dept_map, _ = deps.load_name_maps_func(cur)
  conn.close()

  return build_page_result(
    [workstation_to_dict(row, user_map, dept_map) for row in rows],
    total,
    page_current,
    page_size,
  )


def list_workstations(deps: WorkstationRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_workstation_list_rows(cur)
  user_map, dept_map, _ = deps.load_name_maps_func(cur)
  conn.close()
  return [workstation_to_dict(row, user_map, dept_map) for row in rows]


def get_workstation_detail(deps: WorkstationRouterDeps, *, workstation_id: str) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  row = fetch_workstation_detail_row(cur, workstation_id)
  if not row:
    conn.close()
    raise WorkstationServiceError('工位不存在', 404)
  user_map, dept_map, _ = deps.load_name_maps_func(cur)
  conn.close()
  return workstation_to_dict(row, user_map, dept_map)
