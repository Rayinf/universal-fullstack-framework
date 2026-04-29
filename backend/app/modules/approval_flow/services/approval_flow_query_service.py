from __future__ import annotations

from typing import Any

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.helpers import build_user_name_map, normalize_page_params, process_library_name_map
from app.modules.approval_flow.repositories.approval_flow_node_repo import fetch_approval_flow_nodes
from app.modules.approval_flow.repositories.approval_flow_repo import (
  fetch_approval_flow_detail_row,
  query_approval_flow_list_rows,
  query_approval_flow_page_rows,
  query_approval_flow_page_total,
)
from app.modules.approval_flow.repositories.user_repo import fetch_user_name_rows
from app.modules.approval_flow.serializers import (
  approval_flow_detail_to_dict,
  approval_flow_record_to_dict,
  build_page_result,
)
from app.modules.approval_flow.services.errors import ApprovalFlowServiceError


def query_approval_flow_page(
  deps: ApprovalFlowRouterDeps,
  *,
  current: int,
  size: int,
  keyword: str | None,
  approval_type: int | None,
  status: int | None,
) -> dict[str, Any]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  where_sql = 'WHERE is_deleted = 0'
  values: list[Any] = []
  if keyword and keyword.strip():
    where_sql += ' AND approval_flow_name LIKE ?'
    values.append(f'%{keyword.strip()}%')
  if approval_type is not None:
    where_sql += ' AND approval_type = ?'
    values.append(int(approval_type))
  if status is not None:
    where_sql += ' AND status = ?'
    values.append(int(status))

  page_current, page_size = normalize_page_params(current, size)
  total = int(query_approval_flow_page_total(cur, where_sql, tuple(values))['cnt'])
  rows = query_approval_flow_page_rows(cur, where_sql, tuple(values), page_size, (page_current - 1) * page_size)
  conn.close()
  process_map = process_library_name_map(deps.get_process_library_records_func)
  return build_page_result(
    [approval_flow_record_to_dict(row, process_map) for row in rows],
    total,
    page_current,
    page_size,
  )


def list_approval_flows(deps: ApprovalFlowRouterDeps) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  rows = query_approval_flow_list_rows(cur)
  conn.close()
  process_map = process_library_name_map(deps.get_process_library_records_func)
  return [approval_flow_record_to_dict(row, process_map) for row in rows]


def get_approval_flow_detail(deps: ApprovalFlowRouterDeps, *, approval_flow_id: int) -> list[dict[str, Any]]:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  flow = fetch_approval_flow_detail_row(cur, approval_flow_id)
  if not flow:
    conn.close()
    raise ApprovalFlowServiceError('审批规则不存在', 404)

  user_name_map = build_user_name_map(fetch_user_name_rows(cur))
  nodes = fetch_approval_flow_nodes(cur, approval_flow_id)
  conn.close()
  process_map = process_library_name_map(deps.get_process_library_records_func)
  return [approval_flow_detail_to_dict(flow, node, process_map, user_name_map) for node in nodes]
