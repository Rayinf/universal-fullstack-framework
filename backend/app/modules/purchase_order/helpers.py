from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable

from app.modules.purchase_order.repositories.purchase_order_approval_repo import (
  fetch_approval_flow_nodes,
  fetch_enabled_approval_flow,
  fetch_purchase_order_approval_logs,
)
from app.modules.purchase_order.repositories.user_repo import (
  fetch_role_map,
  fetch_user_name_map,
  fetch_user_role_id,
)


def generate_order_no(prefix: str = 'PO') -> str:
  return f'{prefix}-{datetime.now().strftime("%Y%m%d%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'


def resolve_purchase_approval_flow(cur: Any) -> tuple[int, list[Any]]:
  flow = fetch_enabled_approval_flow(cur, 3)
  if not flow:
    return 0, []

  flow_id = int(flow['id'])
  return flow_id, fetch_approval_flow_nodes(cur, flow_id)


def is_user_allowed_for_node(cur: Any, node: Any, user_id: str) -> bool:
  user_id_text = str(user_id or '').strip()
  if not user_id_text:
    return False

  approval_ids = str(node['approval_ids'] or '').strip()
  if approval_ids:
    id_list = [item.strip() for item in approval_ids.split(',') if item.strip()]
    if user_id_text in id_list:
      return True

  role_id = str(node['role_id'] or '').strip()
  if role_id:
    return fetch_user_role_id(cur, user_id_text) == role_id

  return False


def build_purchase_approval_status(
  order_row: Any,
  cur: Any,
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  order_id = str(order_row['id'])
  order_status = int(order_row['status'] or 0)
  flow_id = safe_int_func(order_row['approval_flow_id'], 0)
  current_node_index = safe_int_func(order_row['current_node_index'], 0)

  nodes = fetch_approval_flow_nodes(cur, flow_id)
  logs = fetch_purchase_order_approval_logs(cur, order_id)
  log_map = {safe_int_func(log['node_index'], 0): log for log in logs}
  role_map = fetch_role_map(cur)
  user_name_map = fetch_user_name_map(cur)

  node_records: list[dict[str, Any]] = []
  for node in nodes:
    node_index = safe_int_func(node['node_index'], 0)
    role_id = str(node['role_id'] or '').strip()
    approval_ids = str(node['approval_ids'] or '').strip()
    approval_id_list = [item.strip() for item in approval_ids.split(',') if item.strip()]
    log_row = log_map.get(node_index)

    if log_row:
      node_status = 2
    elif order_status == 2:
      node_status = 2
    elif order_status == 3:
      node_status = 4
    elif order_status == 1:
      if current_node_index == node_index:
        node_status = 1
      elif current_node_index > node_index:
        node_status = 2
      else:
        node_status = 0
    else:
      node_status = 0

    node_records.append(
      {
        'nodeIndex': node_index,
        'nodeName': node['approval_node_name'] or '',
        'nodeStatus': node_status,
        'roleId': role_id,
        'roleName': role_map.get(role_id, ''),
        'approvalIds': approval_id_list,
        'approvalPeopleName': [user_name_map.get(user_id, user_id) for user_id in approval_id_list],
        'approverId': str(log_row['approver_id'] or '') if log_row else '',
        'approverName': str(log_row['approver_name'] or '') if log_row else '',
        'action': str(log_row['action'] or '') if log_row else '',
        'actionTime': str(log_row['action_time'] or '') if log_row else '',
      },
    )

  return {
    'orderId': order_id,
    'orderNo': order_row['order_no'] or '',
    'orderStatus': order_status,
    'approvalFlowId': flow_id,
    'currentNodeIndex': current_node_index,
    'nodes': node_records,
  }
