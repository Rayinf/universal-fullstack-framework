from __future__ import annotations

from typing import Any, Callable


def build_page_result(records: list[dict[str, Any]], total: int, current: int, size: int) -> dict[str, Any]:
  pages = (total + size - 1) // size if size > 0 else 0
  return {
    'records': records,
    'total': total,
    'size': size,
    'current': current,
    'pages': pages,
  }


def work_order_to_dict(
  row: Any,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'workOrderNo': row['work_order_no'] or '',
    'contractId': row['contract_id'] or '',
    'contractNo': row['contract_no'] or '',
    'customerName': row['customer_name'] or '',
    'productId': row['product_id'] or '',
    'productCode': row['product_code'] or '',
    'productName': row['product_name'] or '',
    'planQuantity': safe_float_func(row['plan_quantity']),
    'reportedQuantity': safe_float_func(row['reported_quantity']),
    'qualifiedQuantity': safe_float_func(row['qualified_quantity']),
    'inboundQuantity': safe_float_func(row['inbound_quantity']),
    'status': safe_int_func(row['status'], 0),
    'priority': safe_int_func(row['priority'], 2),
    'plannedStartDate': row['planned_start_date'] or '',
    'plannedEndDate': row['planned_end_date'] or '',
    'actualStartTime': row['actual_start_time'] or '',
    'actualEndTime': row['actual_end_time'] or '',
    'applicant': row['applicant'] or '',
    'approvalFlowId': safe_int_func(row['approval_flow_id'], 0),
    'currentNodeIndex': safe_int_func(row['current_node_index'], 0),
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }


def work_report_to_dict(row: Any, safe_float_func: Callable[[Any, float], float]) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'workOrderId': row['work_order_id'] or '',
    'workOrderNo': row['work_order_no'] or '',
    'processName': row['process_name'] or '',
    'reportQuantity': safe_float_func(row['report_quantity']),
    'qualifiedQuantity': safe_float_func(row['qualified_quantity']),
    'defectQuantity': safe_float_func(row['defect_quantity']),
    'reportUserId': row['report_user_id'] or '',
    'reportUserName': row['report_user_name'] or '',
    'reportTime': row['report_time'] or '',
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
    'productName': row['product_name'] or '',
    'customerName': row['customer_name'] or '',
  }


def work_inbound_to_dict(row: Any, safe_float_func: Callable[[Any, float], float]) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'inboundNo': row['inbound_no'] or '',
    'workOrderId': row['work_order_id'] or '',
    'workOrderNo': row['work_order_no'] or '',
    'quantity': safe_float_func(row['quantity']),
    'warehouseName': row['warehouse_name'] or '',
    'operatorName': row['operator_name'] or '',
    'inboundTime': row['inbound_time'] or '',
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
    'productName': row['product_name'] or '',
    'customerName': row['customer_name'] or '',
  }
