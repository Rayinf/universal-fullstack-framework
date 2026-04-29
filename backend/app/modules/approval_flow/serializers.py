from __future__ import annotations

from typing import Any


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': (total + size - 1) // size,
  }


def approval_flow_record_to_dict(row: Any, process_map: dict[str, str]) -> dict[str, Any]:
  process_id = str(row['process_library_id'] or '')
  return {
    'id': int(row['id']),
    'approvalFlowName': row['approval_flow_name'] or '',
    'processLibraryId': int(process_id) if process_id.isdigit() else process_id or None,
    'processLibraryName': process_map.get(process_id, ''),
    'approvalType': int(row['approval_type'] or 1),
    'status': int(row['status'] or 1),
    'remarks': row['remarks'] or '',
    'creator': row['creator'] or '',
    'createBy': row['create_by'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def approval_flow_detail_to_dict(
  flow: Any,
  node: Any,
  process_map: dict[str, str],
  user_name_map: dict[str, str],
) -> dict[str, Any]:
  process_id = str(flow['process_library_id'] or '')
  approval_ids = str(node['approval_ids'] or '').strip()
  id_list = [item for item in approval_ids.split(',') if item]
  return {
    'id': int(node['id']),
    'approvalFlowName': flow['approval_flow_name'] or '',
    'approvalFlowId': int(flow['id']),
    'processLibraryId': int(process_id) if process_id.isdigit() else process_id or None,
    'processLibraryName': process_map.get(process_id, ''),
    'status': int(flow['status'] or 1),
    'processFlowRemarks': flow['remarks'] or '',
    'approvalNodeName': node['approval_node_name'] or '',
    'roleId': node['role_id'] or '',
    'approvalIds': approval_ids,
    'approvalPeopleName': [user_name_map.get(user_id, user_id) for user_id in id_list],
    'nodeIndex': int(node['node_index'] or 1),
    'remarks': node['remarks'] or '',
  }


def approval_result_to_dict(
  row: Any,
  process_map: dict[str, str],
  flow_map: dict[int, str],
  user_map: dict[str, str],
) -> dict[str, Any]:
  return {
    'id': int(row['id']),
    'orderId': row['order_id'] or '',
    'resultType': int(row['result_type'] or 2),
    'orderSchedulingId': row['order_scheduling_id'] or '',
    'orderName': row['order_name'] or '',
    'productName': row['product_name'] or '',
    'processLibraryId': row['process_library_id'] or '',
    'processLibraryName': process_map.get(str(row['process_library_id'] or ''), ''),
    'approvalFlowId': int(row['approval_flow_id'] or 0),
    'approvalFlowName': flow_map.get(int(row['approval_flow_id'] or 0), ''),
    'processPeople': row['process_people'] or '',
    'processPeopleName': user_map.get(str(row['process_people'] or ''), ''),
    'approvalStatus': int(row['approval_status'] or 3),
    'approvalRemarks': row['approval_remarks'] or '',
    'createBy': row['process_people'] or '',
    'creator': row['creator'] or '',
    'createTime': row['create_time'] or '',
  }


def approval_result_summary_to_dict(row: Any) -> dict[str, Any]:
  return {
    'id': int(row['id']),
    'orderId': row['order_id'] or '',
    'orderName': row['order_name'] or '',
    'productName': row['product_name'] or '',
    'createTime': row['create_time'] or '',
  }
