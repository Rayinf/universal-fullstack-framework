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


def quotation_to_dict(
  row: Any,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'quoteNo': row['quote_no'] or '',
    'customerId': row['customer_id'] or '',
    'customerName': row['customer_name'] or '',
    'contactPerson': row['contact_person'] or '',
    'totalAmount': safe_float_func(row['total_amount'], 0),
    'discountRate': safe_float_func(row['discount_rate'], 0),
    'finalAmount': safe_float_func(row['final_amount'], 0),
    'validityDays': safe_int_func(row['validity_days'], 30),
    'validityEndDate': row['validity_end_date'] or '',
    'status': safe_int_func(row['status'], 0),
    'applicant': row['applicant'] or '',
    'approvalFlowId': safe_int_func(row['approval_flow_id'], 0),
    'currentNodeIndex': safe_int_func(row['current_node_index'], 0),
    'version': safe_int_func(row['version'], 1),
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }
