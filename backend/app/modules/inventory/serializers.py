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


def inventory_item_to_dict(row: Any, safe_float_func: Callable[[Any, float], float]) -> dict[str, Any]:
  stock_qty = safe_float_func(row['stock_qty'], 0)
  safety_qty = safe_float_func(row['safety_qty'], 0)
  return {
    'id': row['id'],
    'sku': row['sku'],
    'itemName': row['item_name'],
    'unit': row['unit'] or 'pcs',
    'stockQty': stock_qty,
    'safetyQty': safety_qty,
    'isLowStock': stock_qty <= safety_qty,
    'createTime': row['create_time'],
    'updateTime': row['update_time'],
  }


def inventory_tx_to_dict(row: Any, safe_float_func: Callable[[Any, float], float]) -> dict[str, Any]:
  return {
    'id': row['id'],
    'itemId': row['item_id'],
    'sku': row['sku'],
    'itemName': row['item_name'],
    'direction': int(row['direction'] or 1),
    'quantity': safe_float_func(row['quantity'], 0),
    'afterStock': safe_float_func(row['after_stock'], 0),
    'businessNo': row['business_no'] or '',
    'operatorName': row['operator_name'] or '',
    'remark': row['remark'] or '',
    'createTime': row['create_time'],
  }
