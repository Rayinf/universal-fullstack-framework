from __future__ import annotations

from typing import Any, Callable


def build_keyword_filter(keyword: str | None, fields: tuple[str, ...]) -> tuple[str, list[str]]:
  keyword_text = str(keyword or '').strip()
  if not keyword_text:
    return '', []

  sql = ' OR '.join(f'{field} LIKE ?' for field in fields)
  like_value = f'%{keyword_text}%'
  return f' AND ({sql})', [like_value for _ in fields]


def parse_inventory_item_payload(
  payload: dict[str, Any],
  safe_float_func: Callable[[Any, float], float],
) -> dict[str, Any]:
  return {
    'sku': str(payload.get('sku', '')).strip(),
    'item_name': str(payload.get('itemName', '')).strip(),
    'unit': str(payload.get('unit', '')).strip() or 'pcs',
    'stock_qty': safe_float_func(payload.get('stockQty'), 0),
    'safety_qty': safe_float_func(payload.get('safetyQty'), 0),
  }


def parse_inventory_transaction_payload(
  payload: dict[str, Any],
  safe_int_func: Callable[[Any, int], int],
  safe_float_func: Callable[[Any, float], float],
) -> dict[str, Any]:
  return {
    'item_id': str(payload.get('itemId', '') or '').strip(),
    'sku': str(payload.get('sku', '') or '').strip(),
    'direction': safe_int_func(payload.get('direction'), 1),
    'quantity': safe_float_func(payload.get('quantity'), 0),
    'business_no': str(payload.get('businessNo', '')).strip(),
    'operator_name': str(payload.get('operatorName', '')).strip() or '系统管理员',
    'remark': str(payload.get('remark', '')).strip(),
  }
