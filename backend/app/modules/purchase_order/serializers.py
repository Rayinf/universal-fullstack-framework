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


def purchase_order_to_dict(row: Any, safe_float_func: Callable[[Any, float], float]) -> dict[str, Any]:
  return {
    'id': row['id'],
    'orderNo': row['order_no'],
    'supplierName': row['supplier_name'],
    'itemName': row['item_name'],
    'quantity': safe_float_func(row['quantity'], 0),
    'unitPrice': safe_float_func(row['unit_price'], 0),
    'totalAmount': safe_float_func(row['total_amount'], 0),
    'status': int(row['status'] or 0),
    'applicant': row['applicant'] or '',
    'remark': row['remark'] or '',
    'createTime': row['create_time'],
    'updateTime': row['update_time'],
  }
