from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable

from app.modules.work_order.repositories.user_repo import (
  fetch_role_map,
  fetch_user_ids_by_name_or_username,
  fetch_user_ids_by_role,
  fetch_user_name_map,
  fetch_user_role_id,
)
from app.modules.work_order.repositories.work_order_approval_repo import (
  fetch_approval_flow_nodes,
  fetch_enabled_approval_flow,
  fetch_work_order_approval_logs,
)


def generate_work_order_no() -> str:
  return f'WO-{datetime.now().strftime("%Y%m%d%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'


def generate_work_inbound_no() -> str:
  return f'WI-{datetime.now().strftime("%Y%m%d%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'


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


def resolve_work_order_approval_flow(cur: Any, safe_int_func: Callable[[Any, int], int]) -> tuple[int, list[Any]]:
  flow = fetch_enabled_approval_flow(cur, 5)
  if not flow:
    return 0, []

  flow_id = safe_int_func(flow['id'], 0)
  return flow_id, fetch_approval_flow_nodes(cur, flow_id)


def build_work_order_approval_status(
  work_order_row: Any,
  cur: Any,
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  work_order_id = str(work_order_row['id'])
  work_order_status = safe_int_func(work_order_row['status'], 0)
  flow_id = safe_int_func(work_order_row['approval_flow_id'], 0)
  current_node_index = safe_int_func(work_order_row['current_node_index'], 0)

  nodes = fetch_approval_flow_nodes(cur, flow_id)
  logs = fetch_work_order_approval_logs(cur, work_order_id)
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

    if log_row and str(log_row['action'] or '') == 'reject':
      node_status = 3
    elif log_row:
      node_status = 2
    elif work_order_status in (2, 3, 4, 5):
      node_status = 2
    elif work_order_status in (6, 7):
      node_status = 4
    elif work_order_status == 1:
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
        'approvalPeopleName': [user_name_map.get(uid, uid) for uid in approval_id_list],
        'approverId': str(log_row['approver_id'] or '') if log_row else '',
        'approverName': str(log_row['approver_name'] or '') if log_row else '',
        'action': str(log_row['action'] or '') if log_row else '',
        'actionTime': str(log_row['action_time'] or '') if log_row else '',
      },
    )

  return {
    'workOrderId': work_order_id,
    'workOrderNo': work_order_row['work_order_no'] or '',
    'workOrderStatus': work_order_status,
    'approvalFlowId': flow_id,
    'currentNodeIndex': current_node_index,
    'nodes': node_records,
  }


def resolve_work_order_notify_users(cur: Any, applicant_name: str = '') -> list[str]:
  user_ids: list[str] = []
  user_ids.extend(fetch_user_ids_by_role(cur, '1'))

  applicant = applicant_name.strip()
  if applicant:
    user_ids.extend(fetch_user_ids_by_name_or_username(cur, applicant))

  unique_ids: list[str] = []
  seen: set[str] = set()
  for uid in user_ids:
    if uid and uid not in seen:
      seen.add(uid)
      unique_ids.append(uid)
  return unique_ids
