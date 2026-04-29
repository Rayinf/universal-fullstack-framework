from __future__ import annotations

from typing import Any, Callable


def build_keyword_filter(keyword: str | None) -> tuple[str, list[str]]:
  keyword_text = str(keyword or '').strip()
  if not keyword_text:
    return '', []

  where_sql = ' AND (product_code LIKE ? OR product_name LIKE ? OR category LIKE ? OR specification LIKE ?)'
  like_value = f'%{keyword_text}%'
  return where_sql, [like_value, like_value, like_value, like_value]


def parse_product_catalog_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
  safe_float_func: Callable[[Any, float], float],
) -> dict[str, Any]:
  return {
    'product_code': str(payload.get('productCode', '')).strip(),
    'product_name': str(payload.get('productName', '')).strip(),
    'specification': str(payload.get('specification', '')).strip(),
    'unit': str(payload.get('unit', 'pcs')).strip() or 'pcs',
    'reference_price': safe_float_func(payload.get('referencePrice'), 0),
    'cost_price': safe_float_func(payload.get('costPrice'), 0),
    'category': str(payload.get('category', '')).strip(),
    'status': safe_int_func(payload.get('status'), 1),
    'remark': str(payload.get('remark', '')).strip(),
  }
