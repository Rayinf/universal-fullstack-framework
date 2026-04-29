from __future__ import annotations

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.helpers import (
  build_flow_name_map,
  build_user_name_map,
  normalize_page_params,
  process_library_name_map,
)
from app.modules.approval_flow.repositories.approval_flow_repo import query_approval_flow_name_rows
from app.modules.approval_flow.repositories.approval_flow_result_repo import (
  fetch_latest_order_scheduling_result,
  fetch_order_scheduling_result_rows,
  query_approval_flow_result_page_rows,
  query_approval_flow_result_page_total,
  query_recent_approval_result_rows,
)
from app.modules.approval_flow.repositories.user_repo import fetch_user_name_rows
from app.modules.approval_flow.serializers import (
  approval_result_summary_to_dict,
  approval_result_to_dict,
  build_page_result,
)


def query_approval_flow_result_page(
  deps: ApprovalFlowRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  process_people_id: str | None,
  approval_status: int | None,
) -> dict[str, object]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE 1 = 1'
  values: list[object] = []
  if keyword and keyword.strip():
    where_sql += ' AND (order_name LIKE ? OR product_name LIKE ?)'
    key = f'%{keyword.strip()}%'
    values.extend([key, key])
  if process_people_id and process_people_id.strip():
    where_sql += ' AND process_people = ?'
    values.append(process_people_id.strip())
  if approval_status is not None:
    where_sql += ' AND approval_status = ?'
    values.append(int(approval_status))

  page_current, page_size = normalize_page_params(current, size)
  total = int(query_approval_flow_result_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_approval_flow_result_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  process_map = process_library_name_map(deps.get_process_library_records_func)
  flow_map = build_flow_name_map(query_approval_flow_name_rows(cur))
  user_map = build_user_name_map(fetch_user_name_rows(cur))
  conn.close()
  return build_page_result(
    [approval_result_to_dict(row, process_map, flow_map, user_map) for row in rows],
    total,
    page_current,
    page_size,
  )


def get_approval_result_list(
  deps: ApprovalFlowRouterDeps,
  *,
  process_people_id: str,
  approval_status: int,
) -> list[dict[str, object]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE approval_status = ?'
  values: list[object] = [approval_status]
  if process_people_id:
    where_sql += ' AND process_people = ?'
    values.append(process_people_id)
  rows = query_recent_approval_result_rows(cur, where_sql, tuple(values))
  conn.close()
  return [approval_result_summary_to_dict(row) for row in rows]


def get_order_scheduling_result(
  deps: ApprovalFlowRouterDeps,
  *,
  order_scheduling_id: str,
  process_people_id: str | None,
) -> dict[str, object] | None:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE order_scheduling_id = ?'
  values: list[object] = [order_scheduling_id]
  if process_people_id and process_people_id.strip():
    where_sql += ' AND process_people = ?'
    values.append(process_people_id.strip())
  row = fetch_latest_order_scheduling_result(cur, where_sql, tuple(values))
  if not row:
    conn.close()
    return None
  process_map = process_library_name_map(deps.get_process_library_records_func)
  flow_map = build_flow_name_map(query_approval_flow_name_rows(cur))
  user_map = build_user_name_map(fetch_user_name_rows(cur))
  conn.close()
  return approval_result_to_dict(row, process_map, flow_map, user_map)


def get_order_scheduling_result_for_all(
  deps: ApprovalFlowRouterDeps,
  *,
  order_scheduling_id: str,
) -> list[dict[str, object]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = fetch_order_scheduling_result_rows(cur, order_scheduling_id)
  process_map = process_library_name_map(deps.get_process_library_records_func)
  flow_map = build_flow_name_map(query_approval_flow_name_rows(cur))
  user_map = build_user_name_map(fetch_user_name_rows(cur))
  conn.close()
  return [approval_result_to_dict(row, process_map, flow_map, user_map) for row in rows]
