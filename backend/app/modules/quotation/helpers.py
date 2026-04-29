from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable

from app.modules.quotation.repositories.quotation_approval_repo import (
  fetch_approval_flow_nodes,
  fetch_enabled_approval_flow,
  fetch_quotation_approval_logs,
)
from app.modules.quotation.repositories.quotation_item_repo import (
  delete_quotation_items,
  fetch_quotation_items,
  insert_quotation_item,
)
from app.modules.quotation.repositories.user_repo import (
  fetch_role_map,
  fetch_user_name_map,
  fetch_user_role_id,
)


def generate_quote_no() -> str:
  return f'QT-{datetime.now().strftime("%Y%m%d%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'


def resolve_quotation_approval_flow(cur: Any, safe_int_func: Callable[[Any, int], int]) -> tuple[int, list[Any]]:
  flow = fetch_enabled_approval_flow(cur, 4)
  if not flow:
    return 0, []

  flow_id = safe_int_func(flow['id'], 0)
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


def quotation_items_to_list(
  cur: Any,
  quotation_id: str,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> list[dict[str, Any]]:
  rows = fetch_quotation_items(cur, quotation_id)
  result: list[dict[str, Any]] = []
  for row in rows:
    result.append(
      {
        'id': str(row['id']),
        'quotationId': str(row['quotation_id']),
        'productId': row['product_id'] or '',
        'productCode': row['product_code'] or '',
        'productName': row['product_name'] or '',
        'specification': row['specification'] or '',
        'unit': row['unit'] or 'pcs',
        'quantity': safe_float_func(row['quantity'], 0),
        'unitPrice': safe_float_func(row['unit_price'], 0),
        'amount': safe_float_func(row['amount'], 0),
        'sortOrder': safe_int_func(row['sort_order'], 0),
        'remark': row['remark'] or '',
      },
    )
  return result


def save_quotation_items(
  cur: Any,
  quotation_id: str,
  items: list[dict[str, Any]],
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> float:
  delete_quotation_items(cur, quotation_id)
  total = 0.0
  for idx, item in enumerate(items):
    quantity = safe_float_func(item.get('quantity'), 0)
    unit_price = safe_float_func(item.get('unitPrice'), 0)
    amount = round(safe_float_func(item.get('amount'), quantity * unit_price), 2)
    total += amount
    insert_quotation_item(
      cur,
      item_id=str(uuid.uuid4()),
      quotation_id=quotation_id,
      product_id=str(item.get('productId', '') or '').strip(),
      product_code=str(item.get('productCode', '') or '').strip(),
      product_name=str(item.get('productName', '') or '').strip(),
      specification=str(item.get('specification', '') or '').strip(),
      unit=str(item.get('unit', 'pcs') or 'pcs').strip() or 'pcs',
      quantity=quantity,
      unit_price=unit_price,
      amount=amount,
      sort_order=safe_int_func(item.get('sortOrder'), idx + 1),
      remark=str(item.get('remark', '') or '').strip(),
    )
  return round(total, 2)


def build_quotation_approval_status(
  quotation_row: Any,
  cur: Any,
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  quote_id = str(quotation_row['id'])
  quote_status = safe_int_func(quotation_row['status'], 0)
  flow_id = safe_int_func(quotation_row['approval_flow_id'], 0)
  current_node_index = safe_int_func(quotation_row['current_node_index'], 0)

  nodes = fetch_approval_flow_nodes(cur, flow_id)
  logs = fetch_quotation_approval_logs(cur, quote_id)
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
    elif quote_status == 2:
      node_status = 2
    elif quote_status in (3, 5):
      node_status = 4
    elif quote_status == 1:
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
    'quotationId': quote_id,
    'quoteNo': quotation_row['quote_no'] or '',
    'quotationStatus': quote_status,
    'approvalFlowId': flow_id,
    'currentNodeIndex': current_node_index,
    'nodes': node_records,
  }
