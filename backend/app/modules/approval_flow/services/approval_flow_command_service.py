from __future__ import annotations

from typing import Any

from app.modules.approval_flow.deps import ApprovalFlowRouterDeps
from app.modules.approval_flow.repositories.approval_flow_node_repo import (
  delete_approval_flow_nodes,
  insert_approval_flow_node,
)
from app.modules.approval_flow.repositories.approval_flow_repo import (
  fetch_approval_flow_by_id,
  fetch_approval_flow_by_name,
  fetch_other_approval_flow_by_name,
  insert_approval_flow,
  soft_delete_approval_flow,
  update_approval_flow as update_approval_flow_row,
)
from app.modules.approval_flow.services.errors import ApprovalFlowServiceError


def create_approval_flow(
  deps: ApprovalFlowRouterDeps,
  *,
  approval_flow_name: str,
  approval_type: int,
  process_library_id: str,
  status: int,
  remarks: str,
) -> bool:
  if not approval_flow_name:
    raise ApprovalFlowServiceError('规则名称不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if fetch_approval_flow_by_name(cur, approval_flow_name):
    conn.close()
    raise ApprovalFlowServiceError('规则名称已存在', 400)

  insert_approval_flow(
    cur,
    approval_flow_name=approval_flow_name,
    process_library_id=process_library_id if approval_type == 1 else '',
    approval_type=approval_type,
    status=status,
    remarks=remarks,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def update_approval_flow(
  deps: ApprovalFlowRouterDeps,
  *,
  flow_id: int,
  approval_flow_name: str,
  approval_type: int,
  process_library_id: str,
  status: int,
  remarks: str,
) -> bool:
  if flow_id <= 0 or not approval_flow_name:
    raise ApprovalFlowServiceError('参数不完整', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_approval_flow_by_id(cur, flow_id):
    conn.close()
    raise ApprovalFlowServiceError('审批规则不存在', 404)
  if fetch_other_approval_flow_by_name(cur, flow_id, approval_flow_name):
    conn.close()
    raise ApprovalFlowServiceError('规则名称已存在', 400)

  update_approval_flow_row(
    cur,
    flow_id=flow_id,
    approval_flow_name=approval_flow_name,
    process_library_id=process_library_id if approval_type == 1 else '',
    approval_type=approval_type,
    status=status,
    remarks=remarks,
    now=deps.now_str_func(),
  )
  conn.commit()
  conn.close()
  return True


def delete_approval_flow(deps: ApprovalFlowRouterDeps, *, flow_id: int) -> bool:
  conn = deps.get_conn_func()
  cur = conn.cursor()
  soft_delete_approval_flow(cur, flow_id, deps.now_str_func())
  delete_approval_flow_nodes(cur, flow_id)
  conn.commit()
  conn.close()
  return True


def save_approval_flow_nodes(
  deps: ApprovalFlowRouterDeps,
  *,
  payload: list[dict[str, Any]],
) -> bool:
  if not payload:
    return True

  flow_id = deps.safe_int_func(payload[0].get('approvalFlowId'), 0)
  if flow_id <= 0:
    raise ApprovalFlowServiceError('approvalFlowId不能为空', 400)

  conn = deps.get_conn_func()
  cur = conn.cursor()
  if not fetch_approval_flow_by_id(cur, flow_id):
    conn.close()
    raise ApprovalFlowServiceError('审批规则不存在', 404)

  delete_approval_flow_nodes(cur, flow_id)
  now = deps.now_str_func()
  for index, node in enumerate(payload, start=1):
    approval_node_name = str(node.get('approvalNodeName', '')).strip()
    if not approval_node_name:
      continue
    insert_approval_flow_node(
      cur,
      flow_id=flow_id,
      approval_node_name=approval_node_name,
      role_id=str(node.get('roleId', '')).strip(),
      approval_ids=str(node.get('approvalIds', '')).strip(),
      node_index=deps.safe_int_func(node.get('nodeIndex'), index),
      remarks=str(node.get('remarks', '')).strip(),
      now=now,
    )
  conn.commit()
  conn.close()
  return True
