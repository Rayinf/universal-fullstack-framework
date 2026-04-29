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


def product_catalog_to_dict(
  row: Any,
  safe_float_func: Callable[[Any, float], float],
  safe_int_func: Callable[[Any, int], int],
) -> dict[str, Any]:
  return {
    'id': str(row['id']),
    'productCode': row['product_code'] or '',
    'productName': row['product_name'] or '',
    'specification': row['specification'] or '',
    'unit': row['unit'] or 'pcs',
    'referencePrice': safe_float_func(row['reference_price'], 0),
    'costPrice': safe_float_func(row['cost_price'], 0),
    'category': row['category'] or '',
    'status': safe_int_func(row['status'], 1),
    'remark': row['remark'] or '',
    'createTime': row['create_time'] or '',
    'updateTime': row['update_time'] or '',
  }
